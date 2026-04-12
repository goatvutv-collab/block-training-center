import streamlit as st
import streamlit.components.v1 as components
import json
import re

# 1. CONFIGURAÇÃO GOAT TV
st.set_page_config(page_title="GOAT TV - TRAINING CENTER", layout="centered", initial_sidebar_state="collapsed")

# --- LÓGICA DE ARQUÉTIPOS E DESEMPENHO ---
TREINOS_LOGIC = {
    "DRIBLE": {
        "sobe": ["Drible", "Velocidade", "Agilidade"], 
        "desce": ["Desarme", "Força Física"],
        "desc": "Foco em ser 'liso'. Ganha controle curto, mas perde na dividida."
    },
    "PASSE": {
        "sobe": ["Passe Curto", "Visão", "Lançamento"], 
        "desce": ["Aceleração", "Finalização"],
        "desc": "O cérebro do time. Precisão total, mas sacrifica o chute e o arranque."
    },
    "CHUTE": {
        "sobe": ["Finalização", "Força Chute", "Colocação"], 
        "desce": ["Resistência", "Marcação"],
        "desc": "O matador. Foco no gol, mas cansa rápido e não ajuda na zaga."
    }
}

# Inicialização de estado
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = 'LOBBY'
if 'score_final' not in st.session_state:
    st.session_state.score_final = 0

# --- TELA 1: LOBBY CENTRAL ---
if st.session_state.app_mode == 'LOBBY':
    st.markdown("<h1 style='text-align: center; color: #ffd700;'>🎮 LOBBY GOAT TV</h1>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("Configuração")
        player_name = st.text_input("NOME DO ATLETA (Opcional):", "GOAT_PLAYER")
        tipo_treino = st.selectbox("SETOR DE ATIVIDADE:", list(TREINOS_LOGIC.keys()))
        
        st.write("")
        if st.button("ENTRAR NO CAMPO 🏟️", use_container_width=True):
            st.session_state.tipo_selecionado = tipo_treino
            st.session_state.player_name = player_name
            st.session_state.app_mode = 'TRAINING'
            st.rerun()

    with col2:
        st.markdown(f"### 📋 Plano de Treino: {tipo_treino}")
        st.info(TREINOS_LOGIC[tipo_treino]['desc'])
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 📈 DNA")
            for s in TREINOS_LOGIC[tipo_treino]['sobe']:
                st.markdown(f"<span style='color:#0f0'>● {s}</span>", unsafe_allow_html=True)
        with c2:
            st.markdown("##### 📉 TRAVA")
            for d in TREINOS_LOGIC[tipo_treino]['desce']:
                st.markdown(f"<span style='color:#f00'>● {d}</span>", unsafe_allow_html=True)

# --- TELA 2: CAMPO DE TREINAMENTO (G-PERSPECTIVE) ---
elif st.session_state.app_mode == 'TRAINING':
    st.markdown(f"### 🏟️ CT GOAT TV | ATLETA: {st.session_state.player_name}")
    
    tipo = st.session_state.tipo_selecionado
    fases_json = {
        "DRIBLE": """{
            1: {startPos:{x:160, y:410}, gates:[{x1:60,x2:120,y:320},{x1:60,x2:120,y:150},{x1:200,x2:260,y:150},{x1:200,x2:260,y:320}], enemies:[]},
            2: {startPos:{x:160, y:410}, gates:[{x1:40,x2:100,y:350},{x1:220,x2:280,y:250},{x1:40,x2:100,y:150},{x1:130,x2:190,y:80}], enemies:[]},
            3: {startPos:{x:160, y:410}, 
                gates:[{x1:220,x2:280,y:380},{x1:40,x2:100,y:300},{x1:220,x2:280,y:220},{x1:40,x2:100,y:140},{x1:130,x2:190,y:60}], 
                enemies:[
                    {x:100, y:260, range:120, speed:1.4, dir:1}, {x:220, y:260, range:120, speed:1.4, dir:-1},
                    {x:80, y:140, range:150, speed:2.0, dir:1}, {x:240, y:140, range:150, speed:2.0, dir:-1}
                ]}
        }""",
        "PASSE": "{1: {startPos:{x:160, y:410}, gates:[{x1:130,x2:190,y:100}]}, 2: {startPos:{x:160, y:410}, gates:[{x1:40,x2:100,y:150}]}, 3: {startPos:{x:160, y:410}, gates:[{x1:220,x2:280,y:150}]}}",
        "CHUTE": "{1: {startPos:{x:160, y:410}, gates:[{x1:100,x2:220,y:120}]}, 2: {startPos:{x:160, y:410}, gates:[{x1:80,x2:240,y:100}]}, 3: {startPos:{x:160, y:410}, gates:[{x1:140,x2:180,y:80}]}}"
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

        const phases = {fases_json[tipo]};
        const joy = {{ x: 160, y: 530, baseRadius: 45, currX: 160, currY: 530, active: false }};

        function getScale(y) {{ return (y / 460) * 0.55 + 0.45; }}

        function drawCone(x, y, id) {{
            let s = getScale(y);
            let isDown = fallenCones.includes(id);
            if (isDown) {{
                ctx.fillStyle = "rgba(0,0,0,0.3)";
                ctx.beginPath(); ctx.ellipse(x, y, 14*s, 5*s, 0, 0, Math.PI*2); ctx.fill();
            }} else {{
                ctx.fillStyle = "#ff6600";
                ctx.beginPath(); ctx.moveTo(x-8*s, y); ctx.lineTo(x+8*s, y); ctx.lineTo(x, y-22*s); ctx.fill();
            }}
        }}

        function initModule(phase) {{
            gameState = 'COUNTDOWN';
            countdown = 3;
            const config = phases[phase];
            player.x = config.startPos.x; player.y = config.startPos.y;
            ball.x = player.x; ball.y = player.y - 25;
            currentGate = 0; direction = 1;
            modeDisp.innerText = "IDA";
            
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
                        let margin = 20 * getScale(player.y);
                        if(player.x+vx > margin && player.x+vx < 320-margin) player.x += vx;
                        if(player.y+vy > 10 && player.y+vy < 450) player.y += vy;
                        
                        ball.x += (player.x - ball.x) * 0.25;
                        ball.y += (player.y - 22*getScale(player.y) - ball.y) * 0.25;
                    }}
                }}

                let phaseData = phases[currentPhase];
                if(phaseData.enemies) {{
                    phaseData.enemies.forEach(e => {{
                        e.x += e.speed * e.dir;
                        if (Math.abs(e.x - 160) > e.range/2) e.dir *= -1;
                        if (Math.hypot(player.x - e.x, player.y - e.y) < 18*getScale(e.y)) score -= 0.5;
                    }});
                }}

                let phaseGates = phaseData.gates;
                phaseGates.forEach((g, i) => {{
                    let id1 = `p${{currentPhase}}g${{i}}a`, id2 = `p${{currentPhase}}g${{i}}b`;
                    if (!fallenCones.includes(id1) && Math.hypot(player.x-g.x1, player.y-g.y) < 12*getScale(g.y)) {{ fallenCones.push(id1); score -= 50; }}
                    if (!fallenCones.includes(id2) && Math.hypot(player.x-g.x2, player.y-g.y) < 12*getScale(g.y)) {{ fallenCones.push(id2); score -= 50; }}
                }});

                let gate = phaseGates[currentGate];
                if (Math.hypot(ball.x - (gate.x1+gate.x2)/2, ball.y - gate.y) < 25) {{
                    currentGate += direction;
                    if (currentGate >= phaseGates.length) {{ direction = -1; currentGate = phaseGates.length - 2; modeDisp.innerText = "VOLTA"; }}
                    else if (currentGate < 0) {{
                        if (currentPhase < 3) {{ currentPhase++; phaseDisp.innerText = currentPhase+"/3"; initModule(currentPhase); }}
                        else {{ gameState = 'FINISHED'; alert("FIM DE TREINO! SCORE: " + Math.floor(score)); }}
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
            ctx.strokeStyle = "rgba(255,255,255,0.08)";
            for(let i=-100; i<=420; i+=40) {{ ctx.beginPath(); ctx.moveTo(160, -80); ctx.lineTo(i*1.5-80, 460); ctx.stroke(); }}

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
                    drawCone(obj.data.x1, obj.data.y, `p${{currentPhase}}g${{obj.index}}a`);
                    drawCone(obj.data.x2, obj.data.y, `p${{currentPhase}}g${{obj.index}}b`);
                    if (obj.index === currentGate && gameState === 'PLAYING') {{
                        ctx.strokeStyle = direction === 1 ? "#ffd700" : "#0f0";
                        ctx.setLineDash([5,5]); ctx.beginPath(); ctx.moveTo(obj.data.x1, obj.data.y); ctx.lineTo(obj.data.x2, obj.data.y); ctx.stroke(); ctx.setLineDash([]);
                    }}
                }} else if (obj.type === 'enemy') {{
                    ctx.fillStyle="#f00"; ctx.fillRect(obj.data.x-9*s, obj.data.y-28*s, 18*s, 22*s);
                }} else if (obj.type === 'player') {{
                    ctx.fillStyle="#ffd700"; ctx.fillRect(player.x-8*s, player.y-30*s, 16*s, 25*s);
                }} else if (obj.type === 'ball') {{
                    ctx.fillStyle="#fff"; ctx.beginPath(); ctx.arc(ball.x, ball.y, 6*s, 0, Math.PI*2); ctx.fill();
                }}
            }});

            if(gameState === 'COUNTDOWN') {{
                ctx.fillStyle = "rgba(0,0,0,0.8)"; ctx.fillRect(0,0,320,460);
                ctx.fillStyle = "#ffd700"; ctx.font = "bold 50px monospace"; ctx.textAlign = "center";
                ctx.fillText(countdown, 160, 230);
            }}

            ctx.beginPath(); ctx.arc(joy.x, joy.y, 45, 0, Math.PI*2); ctx.strokeStyle='#ffd700'; ctx.stroke();
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
    
    if st.button("SAIR DO TREINO / VOLTAR LOBBY", use_container_width=True):
        st.session_state.app_mode = 'LOBBY'
        st.rerun()

st.sidebar.caption("GOAT TV FEDERATION © 2026")
