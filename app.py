import streamlit as st
import streamlit.components.v1 as components
import json
import os
import re

# 1. CONFIGURAÇÃO INSTITUCIONAL - GOAT TV
st.set_page_config(page_title="GOAT TV - CT ARCADE v8", layout="centered", initial_sidebar_state="collapsed")

# --- SISTEMA DE DADOS E ARQUÉTIPOS ---
DB_FILE = "goat_players.json"

TREINOS_LOGIC = {
    "DRIBLE": {
        "sobe": ["Drible", "Velocidade", "Condução"], 
        "desce": ["Desarme", "Impacto Físico"],
        "desc": "Foco em agilidade e controle. O atleta fica leve, mas perde força defensiva."
    },
    "PASSE": {
        "sobe": ["Passe Rasteiro", "Visão", "Curva"], 
        "desce": ["Aceleração", "Força de Chute"],
        "desc": "Foco na cadência e precisão. O cérebro do time, mas sem explosão física."
    },
    "FINALIZAÇÃO": {
        "sobe": ["Finalização", "Faro de Gol", "Chute Colocado"], 
        "desce": ["Resistência", "Marcação"],
        "desc": "Foco total na rede. O matador que decide, mas não volta pra marcar."
    },
    "DEFESA": {
        "sobe": ["Desarme", "Posicionamento", "Impacto"], 
        "desce": ["Drible", "Velocidade"],
        "desc": "O cão de guarda. Uma muralha física, mas pesado para sair jogando."
    }
}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.player_id = ""
    st.session_state.treino_selecionado = "DRIBLE"

# --- TELA 1: PORTAL DE ACESSO ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #ffd700;'>GOAT TV: PORTAL DE ACESSO</h2>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        pid_input = st.text_input("ID DO ATLETA:", "").strip().upper()
        tipo_treino = st.selectbox("SETOR DE TREINO:", list(TREINOS_LOGIC.keys()))
        
    with col2:
        st.markdown(f"### 📊 Efeito: {tipo_treino}")
        st.caption(TREINOS_LOGIC[tipo_treino]['desc'])
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 📈 SOBE")
            for s in TREINOS_LOGIC[tipo_treino]['sobe']: st.markdown(f"<span style='color:#0f0'>● {s}</span>", unsafe_allow_html=True)
        with c2:
            st.markdown("##### 📉 DESCE")
            for d in TREINOS_LOGIC[tipo_treino]['desce']: st.markdown(f"<span style='color:#f00'>● {d}</span>", unsafe_allow_html=True)

    if st.button("INICIAR TREINAMENTO ARCADE", use_container_width=True):
        if pid_input:
            st.session_state.logged_in = True
            st.session_state.player_id = pid_input
            st.session_state.treino_selecionado = tipo_treino
            st.rerun()

# --- TELA 2: CAMPO DE TREINAMENTO ---
else:
    st.markdown(f"### 🏟️ ATLETA: {st.session_state.player_id} | {st.session_state.treino_selecionado}")
    
    # Configuração de fases: Módulo 3 com 5 PARES DE CONES e Regra de IDA E VOLTA
    fases_json = {
        "DRIBLE": """{
            1: {startPos:{x:160, y:410}, gates:[{x1:60,x2:120,y:320},{x1:200,x2:260,y:320},{x1:130,x2:190,y:150}], enemies:[]},
            2: {startPos:{x:160, y:410}, gates:[{x1:40,x2:100,y:350},{x1:220,x2:280,y:250},{x1:40,x2:100,y:150},{x1:130,x2:190,y:80}], enemies:[]},
            3: {startPos:{x:160, y:410}, 
                gates:[
                    {x1:220,x2:280,y:380}, 
                    {x1:40,x2:100,y:300}, 
                    {x1:220,x2:280,y:220}, 
                    {x1:40,x2:100,y:140}, 
                    {x1:130,x2:190,y:60}
                ], 
                enemies:[
                    {x:160, y:260, range:120, speed:1.2, dir:1},
                    {x:160, y:120, range:150, speed:1.5, dir:-1}
                ]
            }
        }""",
        "PASSE": "{1: {startPos:{x:160, y:410}, gates:[{x1:130,x2:190,y:100}], enemies:[]}, 2: {startPos:{x:160, y:410}, gates:[{x1:40,x2:100,y:150}], enemies:[]}, 3: {startPos:{x:160, y:410}, gates:[{x1:220,x2:280,y:150}], enemies:[]}}",
        "FINALIZACAO": "{1: {startPos:{x:160, y:410}, gates:[{x1:100,x2:220,y:120}], enemies:[]}, 2: {startPos:{x:160, y:410}, gates:[{x1:80,x2:240,y:100}], enemies:[]}, 3: {startPos:{x:160, y:410}, gates:[{x1:140,x2:180,y:80}], enemies:[]}}",
        "DEFESA": "{1: {startPos:{x:160, y:410}, gates:[{x1:40,x2:280,y:230}], enemies:[]}, 2: {startPos:{x:160, y:410}, gates:[{x1:60,x2:260,y:180}], enemies:[]}, 3: {startPos:{x:160, y:410}, gates:[{x1:110,x2:210,y:150}], enemies:[]}}"
    }

    game_code = f"""
    <div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
        <div id="hud" style="color: white; font-family: monospace; margin-bottom: 5px; font-size: 11px; background: #000; padding: 5px 15px; border-radius: 10px; border: 1px solid #ffd700; width: 300px; display: flex; justify-content: space-between;">
            <span>ETAPA: <b id="phaseDisp" style="color: #0f0;">1/3</b></span>
            <span>MODO: <b id="modeDisp" style="color: #ffd700;">IDA</b></span>
            <span>SCORE: <b id="scoreDisp" style="color: #0f0;">1000</b></span>
        </div>
        <canvas id="gameCanvas" width="320" height="600" style="background: #111; border: 4px solid #333; border-radius: 10px; touch-action: none;"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreDisp = document.getElementById('scoreDisp');
        const phaseDisp = document.getElementById('phaseDisp');
        const modeDisp = document.getElementById('modeDisp');

        let player = {{ x: 160, y: 410, speed: 1.5 }};
        let ball = {{ x: 160, y: 385 }};
        let score = 1000;
        let currentPhase = 1;
        let currentGate = 0;
        let direction = 1; // 1 = IDA, -1 = VOLTA
        let gameState = 'COUNTDOWN';
        let countdown = 3;
        let fallenCones = [];

        const phases = {fases_json[st.session_state.treino_selecionado]};
        const joy = {{ x: 160, y: 530, baseRadius: 45, currX: 160, currY: 530, active: false }};

        function getScale(y) {{ return (y / 460) * 0.55 + 0.45; }}

        function initModule(phase) {{
            gameState = 'COUNTDOWN';
            countdown = 3;
            const config = phases[phase];
            player.x = config.startPos.x;
            player.y = config.startPos.y;
            ball.x = player.x; ball.y = player.y - 25;
            currentGate = 0; direction = 1;
            modeDisp.innerText = "IDA"; modeDisp.style.color = "#ffd700";
            
            let timer = setInterval(() => {{
                countdown--;
                if(countdown <= 0) {{ clearInterval(timer); gameState = 'PLAYING'; }}
            }}, 1000);
        }}

        function update() {{
            if (gameState === 'FINISHED') return;

            if (gameState === 'PLAYING') {{
                if (joy.active) {{
                    let dx = joy.currX - joy.x, dy = joy.currY - joy.y, d = Math.hypot(dx, dy);
                    if (d > 3) {{ 
                        let vx = (dx/d)*player.speed, vy = (dy/d)*player.speed;
                        let nextX = player.x + vx, nextY = player.y + vy;
                        let margin = 20 * getScale(player.y);
                        
                        // PAREDES REAIS
                        if(nextX > margin && nextX < 320 - margin) player.x = nextX;
                        if(nextY > margin && nextY < 450) player.y = nextY;
                        
                        ball.x += (player.x - ball.x) * 0.25;
                        ball.y += (player.y - 22*getScale(player.y) - ball.y) * 0.25;
                    }}
                }}

                let phaseData = phases[currentPhase];
                if(phaseData.enemies) {{
                    phaseData.enemies.forEach(e => {{
                        e.x += e.speed * e.dir;
                        if (Math.abs(e.x - 160) > e.range/2) e.dir *= -1;
                        if (Math.hypot(player.x - e.x, player.y - e.y) < 18*getScale(e.y)) score -= 0.4;
                    }});
                }}

                let phaseGates = phaseData.gates;
                let gate = phaseGates[currentGate];
                if (Math.hypot(ball.x - (gate.x1+gate.x2)/2, ball.y - gate.y) < 25) {{
                    currentGate += direction;
                    
                    // REGRA BATE E VOLTA
                    if (currentGate >= phaseGates.length) {{
                        direction = -1; currentGate = phaseGates.length - 2;
                        modeDisp.innerText = "VOLTA"; modeDisp.style.color = "#0f0";
                    }} else if (currentGate < 0) {{
                        if (currentPhase < 3) {{
                            currentPhase++; phaseDisp.innerText = currentPhase + "/3";
                            initModule(currentPhase);
                        }} else {{
                            gameState = 'FINISHED';
                            alert("TREINO CONCLUÍDO! SCORE: " + Math.floor(score));
                        }}
                    }}
                }}
            }}
            scoreDisp.innerText = Math.floor(score);
            render();
            requestAnimationFrame(update);
        }}

        function render() {{
            ctx.fillStyle = '#1e3d1a'; ctx.fillRect(0,0,320,460);
            ctx.fillStyle = '#050505'; ctx.fillRect(0,460,320,140);
            
            // PERSPECTIVA G-PERSPECTIVE
            ctx.strokeStyle = "rgba(255,255,255,0.08)"; ctx.lineWidth = 1;
            for(let i=-100; i<=420; i+=40) {{
                ctx.beginPath(); ctx.moveTo(160, -80); ctx.lineTo(i*1.5 - 80, 460); ctx.stroke();
            }}

            let phaseData = phases[currentPhase];
            let drawList = [];
            phaseData.gates.forEach((g, i) => drawList.push({{ type: 'gate', y: g.y, data: g, index: i }}));
            if(phaseData.enemies) phaseData.enemies.forEach(e => drawList.push({{ type: 'enemy', y: e.y, data: e }}));
            drawList.push({{ type: 'player', y: player.y }});
            drawList.push({{ type: 'ball', y: ball.y }});
            drawList.sort((a, b) => a.y - b.y);

            drawList.forEach(obj => {{
                let s = getScale(obj.y);
                if (obj.type === 'gate') {{
                    ctx.fillStyle = "#ff6600";
                    ctx.beginPath(); ctx.moveTo(obj.data.x1-8*s, obj.data.y); ctx.lineTo(obj.data.x1+8*s, obj.data.y); ctx.lineTo(obj.data.x1, obj.data.y-22*s); ctx.fill();
                    ctx.beginPath(); ctx.moveTo(obj.data.x2-8*s, obj.data.y); ctx.lineTo(obj.data.x2+8*s, obj.data.y); ctx.lineTo(obj.data.x2, obj.data.y-22*s); ctx.fill();
                    if (obj.index === currentGate && gameState === 'PLAYING') {{
                        ctx.strokeStyle = direction === 1 ? "#ffd700" : "#0f0";
                        ctx.setLineDash([5, 5]); ctx.beginPath();
                        ctx.moveTo(obj.data.x1, obj.data.y); ctx.lineTo(obj.data.x2, obj.data.y); ctx.stroke(); ctx.setLineDash([]);
                    }}
                }} else if (obj.type === 'enemy') {{
                    ctx.fillStyle="rgba(0,0,0,0.3)"; ctx.beginPath(); ctx.ellipse(obj.data.x, obj.data.y, 14*s, 6*s, 0, 0, Math.PI*2); ctx.fill();
                    ctx.fillStyle="#f00"; ctx.fillRect(obj.data.x-9*s, obj.data.y-28*s, 18*s, 22*s);
                }} else if (obj.type === 'player') {{
                    ctx.fillStyle="rgba(0,0,0,0.3)"; ctx.beginPath(); ctx.ellipse(player.x, player.y, 12*s, 5*s, 0, 0, Math.PI*2); ctx.fill();
                    ctx.fillStyle="#ffd700"; ctx.fillRect(player.x-8*s, player.y-30*s, 16*s, 25*s);
                    ctx.fillStyle="#d2b48c"; ctx.beginPath(); ctx.arc(player.x, player.y-35*s, 7*s, 0, Math.PI*2); ctx.fill();
                }} else if (obj.type === 'ball') {{
                    ctx.fillStyle="white"; ctx.beginPath(); ctx.arc(ball.x, ball.y, 6*s, 0, Math.PI*2); ctx.fill();
                    ctx.strokeStyle="#000"; ctx.stroke();
                }}
            }});

            if(gameState === 'COUNTDOWN') {{
                ctx.fillStyle = "rgba(0,0,0,0.85)"; ctx.fillRect(0,0,320,460);
                ctx.fillStyle = "#ffd700"; ctx.font = "bold 50px monospace"; ctx.textAlign = "center";
                ctx.fillText(countdown, 160, 230);
            }}

            // ANALÓGICO ARCADE CENTRALIZADO
            ctx.beginPath(); ctx.arc(joy.x, joy.y, 45, 0, Math.PI*2); ctx.strokeStyle='#ffd700'; ctx.lineWidth=2; ctx.stroke();
            ctx.beginPath(); ctx.arc(joy.currX, joy.currY, 20, 0, Math.PI*2); ctx.fillStyle='#ffd700'; ctx.fill();
        }}

        canvas.addEventListener('pointerdown', e => {{ const r=canvas.getBoundingClientRect(); if(Math.hypot(e.clientX-r.left-joy.x, e.clientY-r.top-joy.y)<60) joy.active=true; }});
        canvas.addEventListener('pointermove', e => {{ if(!joy.active) return; const r=canvas.getBoundingClientRect(); let dx=e.clientX-r.left-joy.x, dy=e.clientY-r.top-joy.y, d=Math.min(Math.hypot(dx,dy),45), a=Math.atan2(dy,dx); joy.currX=joy.x+Math.cos(a)*d; joy.currY=joy.y+Math.sin(a)*d; }});
        canvas.addEventListener('pointerup', () => {{ joy.active=false; joy.currX=joy.x; joy.currY=joy.y; }});
        
        initModule(1);
        update();
    </script>
    """

    components.html(game_code, height=650)
    
    if st.button("FINALIZAR E SALVAR", use_container_width=True):
        st.success(f"Resultados de {st.session_state.player_id} registrados!")
        st.session_state.logged_in = False
        st.rerun()

st.sidebar.caption("GOAT TV ARCADE CT v8.0")
