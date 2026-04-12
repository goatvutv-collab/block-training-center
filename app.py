import streamlit as st
import streamlit.components.v1 as components
import json
import os
import re

# 1. CONFIGURAÇÃO INSTITUCIONAL - GOAT TV
st.set_page_config(page_title="GOAT TV - CT G-PERSPECTIVE", layout="centered", initial_sidebar_state="collapsed")

# --- SISTEMA DE DADOS E ARQUÉTIPOS ---
DB_FILE = "goat_players.json"

TREINOS_LOGIC = {
    "DRIBLE": {"sobe": ["drible", "aceleracao", "controle_bola"], "desce": ["desarme", "agressividade"]},
    "PASSE":  {"sobe": ["passe_rasteiro", "passe_alto", "curva"], "desce": ["velocidade", "forca_chute"]},
    "FINALIZACAO": {"sobe": ["finalizacao", "forca_chute", "talento_ofensivo"], "desce": ["resistencia", "desarme"]},
    "DEFESA": {"sobe": ["talento_defensivo", "desarme", "contato_fisico"], "desce": ["drible", "aceleracao"]}
}

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.player_id = ""
    st.session_state.treino_selecionado = "DRIBLE"

# --- TELA 1: PORTAL DE ACESSO ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #ffd700; font-family: sans-serif;'>GOAT TV: PORTAL DE ACESSO</h2>", unsafe_allow_html=True)
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        pid_input = st.text_input("ID DO ATLETA:", "").strip().upper()
    with col2:
        tipo_treino = st.selectbox("SETOR DE TREINO:", list(TREINOS_LOGIC.keys()))
    
    if st.button("INICIAR TREINAMENTO", use_container_width=True):
        if pid_input and bool(re.match("^[a-zA-Z0-9]*$", pid_input)):
            st.session_state.logged_in = True
            st.session_state.player_id = pid_input
            st.session_state.treino_selecionado = tipo_treino
            st.rerun()
        else:
            st.error("ID Inválido.")

# --- TELA 2: CAMPO DE TREINAMENTO (G-PERSPECTIVE 2.5D ATUALIZADO) ---
else:
    st.markdown(f"### 🏟️ ATLETA: {st.session_state.player_id} | SETOR: {st.session_state.treino_selecionado}")
    
    # Configuração de fases com POSIÇÃO INICIAL (startPos) específica para cada módulo
    fases_json = {
        "DRIBLE": """{
            1: {startPos:{x:160, y:410}, gates:[{x1:60,x2:120,y:320},{x1:60,x2:120,y:150},{x1:200,x2:260,y:150},{x1:200,x2:260,y:320}], enemies:[]},
            2: {startPos:{x:60, y:410}, gates:[{x1:40,x2:100,y:320},{x1:130,x2:190,y:200},{x1:220,x2:280,y:80}], enemies:[]},
            3: {startPos:{x:160, y:410}, gates:[{x1:130,x2:190,y:60}], enemies:[{x:160, y:280, range:100, speed:2, dir:1}, {x:160, y:150, range:140, speed:3, dir:-1}]}
        }""",
        "PASSE": "{1: {startPos:{x:160, y:410}, gates:[{x1:130,x2:190,y:100}]}, 2: {startPos:{x:160, y:410}, gates:[{x1:40,x2:100,y:150}]}, 3: {startPos:{x:160, y:410}, gates:[{x1:220,x2:280,y:150}]}}",
        "FINALIZACAO": "{1: {startPos:{x:160, y:410}, gates:[{x1:100,x2:220,y:120}]}, 2: {startPos:{x:160, y:410}, gates:[{x1:80,x2:240,y:100}]}, 3: {startPos:{x:160, y:410}, gates:[{x1:140,x2:180,y:80}]}}",
        "DEFESA": "{1: {startPos:{x:160, y:410}, gates:[{x1:40,x2:280,y:230}]}, 2: {startPos:{x:160, y:410}, gates:[{x1:60,x2:260,y:180}]}, 3: {startPos:{x:160, y:410}, gates:[{x1:110,x2:210,y:150}]}}"
    }

    game_code = f"""
    <div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
        <div id="hud" style="color: white; font-family: monospace; margin-bottom: 8px; font-size: 11px; background: rgba(0,0,0,0.9); padding: 5px 15px; border-radius: 20px; border: 1px solid #ffd700; width: 300px; display: flex; justify-content: space-between;">
            <span>ID: <b style="color: #ffd700;">{st.session_state.player_id}</b></span>
            <span>ETAPA: <b id="phaseDisp" style="color: #0f0;">1/3</b></span>
            <span>SCORE: <b id="scoreDisp" style="color: #0f0;">1000</b></span>
        </div>
        <canvas id="gameCanvas" width="320" height="460" style="background: #1e3d1a; border: 4px solid #333; border-radius: 10px; touch-action: none;"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreDisp = document.getElementById('scoreDisp');
        const phaseDisp = document.getElementById('phaseDisp');

        // VELOCIDADE CONTROLADA
        let player = {{ x: 160, y: 410, speed: 2.8 }};
        let ball = {{ x: 160, y: 385 }};
        let score = 1000;
        let currentPhase = 1;
        let currentGate = 0;
        let direction = 1; 
        let gameState = 'COUNTDOWN'; // PLAYING, COUNTDOWN, FINISHED
        let countdown = 3;
        let fallenCones = [];

        const phases = {fases_json[st.session_state.treino_selecionado]};
        const joy = {{ x: 60, y: 385, baseRadius: 35, currX: 60, currY: 385, active: false }};

        // A LINHA MÁGICA DA PERSPECTIVA GOAT TV
        function getScale(y) {{ return (y / 460) * 0.55 + 0.45; }}

        function initModule(phase) {{
            gameState = 'COUNTDOWN';
            countdown = 3;
            const config = phases[phase];
            player.x = config.startPos.x;
            player.y = config.startPos.y;
            ball.x = player.x;
            ball.y = player.y - 25;
            currentGate = 0;
             fallenCones = [];
            
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
                    if (d > 0) {{
                        let vx = (dx/d)*player.speed, vy = (dy/d)*player.speed;
                        
                        // COLISÃO COM PAREDE E LIMITES DO CANÁRIO G-PERSPECTIVE
                        let nextX = player.x + vx;
                        let nextY = player.y + vy;
                        let margin = 15 * getScale(player.y);
                        
                        if(nextX > margin && nextX < 320 - margin) player.x = nextX;
                        if(nextY > margin && nextY < 460 - margin) player.y = nextY;
                        
                        ball.x += (player.x - ball.x) * 0.2;
                        ball.y += (player.y - 20*getScale(player.y) - ball.y) * 0.2;
                    }}
                }}

                let phaseData = phases[currentPhase];
                if(phaseData.enemies) {{
                    phaseData.enemies.forEach(e => {{
                        e.x += e.speed * e.dir;
                        if (Math.abs(e.x - 160) > e.range/2) e.dir *= -1;
                    }});
                }}

                // Cones Colisão
                let phaseGates = phaseData.gates;
                phaseGates.forEach((g, i) => {{
                    let id1 = `p${{currentPhase}}g${{i}}a`, id2 = `p${{currentPhase}}g${{i}}b`;
                    let s = getScale(g.y);
                    if (!fallenCones.includes(id1) && Math.hypot(player.x-g.x1, player.y-g.y) < 14*s) {{ fallenCones.push(id1); score -= 50; }}
                    if (!fallenCones.includes(id2) && Math.hypot(player.x-g.x2, player.y-g.y) < 14*s) {{ fallenCones.push(id2); score -= 50; }}
                }});

                // Passagem de Portão e Troca de Módulo
                let gate = phaseGates[currentGate];
                if (Math.hypot(ball.x - (gate.x1+gate.x2)/2, ball.y - gate.y) < 25) {{
                    currentGate++;
                    if (currentGate >= phaseGates.length) {{
                        if (currentPhase < 3) {{
                            currentPhase++;
                            phaseDisp.innerText = currentPhase + "/3";
                            initModule(currentPhase); // VOLTA PARA BAIXO E CONTAGEM
                        }} else {{
                            gameState = 'FINISHED';
                            alert("FIM DE TREINO! SCORE: " + Math.floor(score));
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
            
            // Desenho do Gramado (G-PERSPECTIVE 2.5D)
            ctx.strokeStyle = "rgba(255,255,255,0.06)"; ctx.lineWidth = 1;
            for(let i=-50; i<=370; i+=40) {{
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
                    // Desenho dos Cones com Distorção de Perspectiva
                    ctx.fillStyle = fallenCones.includes(`p${{currentPhase}}g${{obj.index}}a`) ? "rgba(0,0,0,0.2)" : "#ff6600";
                    ctx.beginPath(); ctx.moveTo(obj.data.x1-8*s, obj.data.y); ctx.lineTo(obj.data.x1+8*s, obj.data.y); ctx.lineTo(obj.data.x1, obj.data.y-22*s); ctx.fill();
                    ctx.fillStyle = fallenCones.includes(`p${{currentPhase}}g${{obj.index}}b`) ? "rgba(0,0,0,0.2)" : "#ff6600";
                    ctx.beginPath(); ctx.moveTo(obj.data.x2-8*s, obj.data.y); ctx.lineTo(obj.data.x2+8*s, obj.data.y); ctx.lineTo(obj.data.x2, obj.data.y-22*s); ctx.fill();
                    
                    if (obj.index === currentGate && gameState === 'PLAYING') {{
                        ctx.strokeStyle = "rgba(0,255,0,0.5)"; ctx.setLineDash([5, 5]);
                        ctx.beginPath(); ctx.moveTo(obj.data.x1, obj.data.y); ctx.lineTo(obj.data.x2, obj.data.y); ctx.stroke();
                        ctx.setLineDash([]);
                    }}
                }} else if (obj.type === 'enemy') {{
                    ctx.fillStyle="rgba(0,0,0,0.3)"; ctx.beginPath(); ctx.ellipse(obj.data.x, obj.data.y, 14*s, 6*s, 0, 0, Math.PI*2); ctx.fill();
                    ctx.fillStyle="#f00"; ctx.fillRect(obj.data.x-9*s, obj.data.y-28*s, 18*s, 22*s);
                }} else if (obj.type === 'player') {{
                    ctx.fillStyle="rgba(0,0,0,0.3)"; ctx.beginPath(); ctx.ellipse(player.x, player.y, 12*s, 5*s, 0, 0, Math.PI*2); ctx.fill();
                    ctx.fillStyle="#ffd700"; ctx.fillRect(player.x-8*s, player.y-28*s, 16*s, 22*s);
                    ctx.fillStyle="#d2b48c"; ctx.beginPath(); ctx.arc(player.x, player.y-35*s, 7*s, 0, Math.PI*2); ctx.fill();
                }} else if (obj.type === 'ball') {{
                    ctx.fillStyle="white"; ctx.beginPath(); ctx.arc(ball.x, ball.y, 6*s, 0, Math.PI*2); ctx.fill();
                    ctx.strokeStyle="#000"; ctx.lineWidth=1; ctx.stroke();
                }}
            }});

            if(gameState === 'COUNTDOWN') {{
                ctx.fillStyle = "rgba(0,0,0,0.7)"; ctx.fillRect(0,0,320,460);
                ctx.fillStyle = "#ffd700"; ctx.font = "bold 40px monospace"; ctx.textAlign = "center";
                ctx.fillText(countdown, 160, 230);
                ctx.font = "12px monospace"; ctx.fillText("REPOSICIONANDO ATLETA...", 160, 260);
            }}

            // Joystick
            ctx.beginPath(); ctx.arc(joy.x, joy.y, 35, 0, Math.PI*2); ctx.fillStyle='rgba(255,255,255,0.1)'; ctx.fill();
            ctx.beginPath(); ctx.arc(joy.currX, joy.currY, 15, 0, Math.PI*2); ctx.fillStyle='#0f0'; ctx.fill();
        }}

        canvas.addEventListener('pointerdown', e => {{ const r=canvas.getBoundingClientRect(); if(Math.hypot(e.clientX-r.left-joy.x, e.clientY-r.top-joy.y)<50) joy.active=true; }});
        canvas.addEventListener('pointermove', e => {{ if(!joy.active) return; const r=canvas.getBoundingClientRect(); let dx=e.clientX-r.left-joy.x, dy=e.clientY-r.top-joy.y, d=Math.min(Math.hypot(dx,dy),35), a=Math.atan2(dy,dx); joy.currX=joy.x+Math.cos(a)*d; joy.currY=joy.y+Math.sin(a)*d; }});
        canvas.addEventListener('pointerup', () => {{ joy.active=false; joy.currX=joy.x; joy.currY=joy.y; }});
        
        initModule(1);
        update();
    </script>
    """

    components.html(game_code, height=540)
