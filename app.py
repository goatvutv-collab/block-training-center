import streamlit as st
import streamlit.components.v1 as components
import json
import os
import re

# 1. CONFIGURAÇÃO INSTITUCIONAL - GOAT TV
st.set_page_config(page_title="GOAT TV - CT PERSPECTIVA", layout="centered", initial_sidebar_state="collapsed")

# --- SISTEMA DE DADOS ---
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

# --- TELA 1: PORTAL ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #ffd700;'>GOAT TV: PORTAL DE ACESSO</h2>", unsafe_allow_html=True)
    st.write("---")
    pid_input = st.text_input("ID DO ATLETA:", "").strip().upper()
    tipo_treino = st.selectbox("SETOR:", list(TREINOS_LOGIC.keys()))
    if st.button("INICIAR TREINAMENTO"):
        if pid_input:
            st.session_state.logged_in = True
            st.session_state.player_id = pid_input
            st.session_state.treino_selecionado = tipo_treino
            st.rerun()

# --- TELA 2: CAMPO DE TREINAMENTO ---
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
    <div style="display: flex; justify-content: center; flex-direction: column; align-items: center;">
        <div id="hud" style="color: white; font-family: monospace; margin-bottom: 5px; font-size: 11px; background: #000; padding: 5px 15px; border: 1px solid #ffd700; border-radius: 10px; width: 310px; display: flex; justify-content: space-between;">
            <span>ETAPA: <b id="phaseDisp" style="color: #0f0;">1/3</b></span>
            <span>SCORE: <b id="scoreDisp" style="color: #0f0;">1000</b></span>
        </div>
        <canvas id="gameCanvas" width="320" height="460" style="background: #1e3d1a; border: 5px solid #222; border-radius: 5px;"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreDisp = document.getElementById('scoreDisp');
        const phaseDisp = document.getElementById('phaseDisp');

        const phases = {fases_json[st.session_state.treino_selecionado]};
        let currentPhase = 1;
        let gameState = 'COUNTDOWN'; // PLAYING, COUNTDOWN, FINISHED
        let countdown = 3;
        let score = 1000;
        let player = {{ x: 160, y: 410, speed: 2.8 }};
        let ball = {{ x: 160, y: 385 }};
        let currentGate = 0;
        let fallenCones = [];
        let joy = {{ x: 60, y: 385, baseRadius: 35, currX: 60, currY: 385, active: false }};

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
            
            let timer = setInterval(() => {{
                countdown--;
                if(countdown <= 0) {{ clearInterval(timer); gameState = 'PLAYING'; }}
            }}, 1000);
        }}

        function update() {{
            if (gameState === 'PLAYING') {{
                if (joy.active) {{
                    let dx = joy.currX - joy.x, dy = joy.currY - joy.y, d = Math.hypot(dx, dy);
                    if (d > 0) {{
                        let vx = (dx/d)*player.speed, vy = (dy/d)*player.speed;
                        
                        // COLISÃO COM PAREDE (Limites do Quadrado)
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

                let gate = phaseData.gates[currentGate];
                if (Math.hypot(ball.x - (gate.x1+gate.x2)/2, ball.y - gate.y) < 25) {{
                    currentGate++;
                    if (currentGate >= phaseData.gates.length) {{
                        if (currentPhase < 3) {{
                            currentPhase++;
                            phaseDisp.innerText = currentPhase + "/3";
                            initModule(currentPhase);
                        }} else {{
                            gameState = 'FINISHED';
                            alert("FIM DE TREINO! SCORE: " + Math.floor(score));
                        }}
                    }}
                }}
            }}
            render();
            requestAnimationFrame(update);
        }}

        function render() {{
            ctx.fillStyle = '#1e3d1a'; ctx.fillRect(0,0,320,460);
            
            // Desenho do Gramado e Paredes Visuais
            ctx.strokeStyle = "rgba(0,0,0,0.5)"; ctx.lineWidth = 10;
            ctx.strokeRect(0,0,320,460); // Moldura do campo

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
                    ctx.fillRect(obj.data.x1-5*s, obj.data.y-5*s, 10*s, 10*s);
                    ctx.fillRect(obj.data.x2-5*s, obj.data.y-5*s, 10*s, 10*s);
                    if(obj.index === currentGate) {{
                        ctx.strokeStyle="#0f0"; ctx.setLineDash([5,5]);
                        ctx.beginPath(); ctx.moveTo(obj.data.x1, obj.data.y); ctx.lineTo(obj.data.x2, obj.data.y); ctx.stroke();
                        ctx.setLineDash([]);
                    }}
                }} else if (obj.type === 'player') {{
                    ctx.fillStyle="#ffd700"; ctx.fillRect(player.x-8*s, player.y-25*s, 16*s, 22*s);
                }} else if (obj.type === 'enemy') {{
                    ctx.fillStyle="#f00"; ctx.fillRect(obj.data.x-8*s, obj.data.y-25*s, 16*s, 22*s);
                }} else if (obj.type === 'ball') {{
                    ctx.fillStyle="#fff"; ctx.beginPath(); ctx.arc(ball.x, ball.y, 6*s, 0, Math.PI*2); ctx.fill();
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
