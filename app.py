import streamlit as st
import streamlit.components.v1 as components
import json
import os
import re

# 1. CONFIGURAÇÃO INSTITUCIONAL - GOAT TV
st.set_page_config(page_title="GOAT TV - CT PERSPECTIVA", layout="centered", initial_sidebar_state="collapsed")

# --- SISTEMA DE REGISTRO ---
DB_FILE = "goat_players.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.player_id = ""

# --- TELA 1: PORTAL ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #ffd700; font-family: sans-serif;'>GOAT TV: PORTAL DE ACESSO</h2>", unsafe_allow_html=True)
    st.write("---")
    pid_input = st.text_input("ID DO ATLETA:", "").strip().upper()
    if st.button("INICIAR TREINAMENTO"):
        if pid_input and bool(re.match("^[a-zA-Z0-9]*$", pid_input)):
            data = load_data()
            if pid_input not in data:
                data[pid_input] = {"best_score": 0}
                save_data(data)
            st.session_state.logged_in = True
            st.session_state.player_id = pid_input
            st.rerun()
        else:
            st.error("ID Inválido.")

# --- TELA 2: CAMPO DE TREINAMENTO ---
else:
    st.markdown(f"### 🏟️ ATLETA: {st.session_state.player_id}")
    
    game_code = f"""
    <div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
        <div id="hud" style="color: white; font-family: monospace; margin-bottom: 8px; font-size: 11px; background: rgba(0,0,0,0.8); padding: 5px 15px; border-radius: 20px; border: 1px solid #444; width: 300px; display: flex; justify-content: space-between;">
            <span>ID: <b style="color: #ffd700;">{st.session_state.player_id}</b></span>
            <span>ETAPA: <b id="phaseDisp" style="color: #0f0;">1/2</b></span>
            <span>SCORE: <b id="scoreDisp" style="color: #0f0;">1000</b></span>
        </div>
        <canvas id="gameCanvas" width="320" height="460" style="background: #1e3d1a; border: 2px solid #555; border-radius: 10px; touch-action: none;"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreDisp = document.getElementById('scoreDisp');
        const phaseDisp = document.getElementById('phaseDisp');

        let player = {{ x: 160, y: 410, speed: 3.8 }};
        let ball = {{ x: 160, y: 385, radius: 7 }};
        let score = 1000;
        let currentPhase = 1;
        let currentGate = 0;
        let direction = 1; 
        let gameState = 'PLAYING';
        let wobble = 0;

        // Circuitos: 1 (U) e 2 (Zig-Zag em 3 verticais)
        const phases = {{
            1: {{ gates: [{{x1: 60, x2: 120, y: 320}}, {{x1: 60, x2: 120, y: 150}}, {{x1: 200, x2: 260, y: 150}}, {{x1: 200, x2: 260, y: 320}}] }},
            2: {{ gates: [{{x1: 40, x2: 100, y: 320}}, {{x1: 130, x2: 190, y: 200}}, {{x1: 220, x2: 280, y: 80}}] }}
        }};

        let fallenCones = [];
        const joy = {{ x: 60, y: 380, baseRadius: 35, stickRadius: 18, currX: 60, currY: 380, active: false }};

        function getScale(y) {{ return (y / 460) * 0.55 + 0.45; }}

        function drawCone(x, y, id) {{
            let s = getScale(y);
            let isDown = fallenCones.includes(id);
            if (isDown) {{
                ctx.fillStyle = "rgba(100,50,0,0.3)";
                ctx.beginPath(); ctx.ellipse(x, y, 14*s, 4*s, 0, 0, Math.PI*2); ctx.fill();
            }} else {{
                ctx.fillStyle = "#ff6600";
                ctx.beginPath(); ctx.moveTo(x-9*s, y); ctx.lineTo(x+9*s, y); ctx.lineTo(x, y-25*s); ctx.fill();
                ctx.fillStyle = "#222"; ctx.fillRect(x-10*s, y-1, 20*s, 2);
            }}
        }}

        function update() {{
            if (gameState !== 'PLAYING') return;

            if (joy.active) {{
                let dx = joy.currX - joy.x, dy = joy.currY - joy.y, d = Math.hypot(dx, dy);
                if (d > 0) {{
                    let vx = (dx/d)*player.speed, vy = (dy/d)*player.speed;
                    player.x += vx; player.y += vy;
                    
                    wobble += 0.25;
                    // A bola segue o pé com leve ginga
                    let targetX = player.x + vx*5 + Math.cos(wobble)*3;
                    let targetY = player.y + vy*5;
                    ball.x += (targetX - ball.x) * 0.2;
                    ball.y += (targetY - ball.y) * 0.2;
                }}
            }}

            let currentGates = phases[currentPhase].gates;
            currentGates.forEach((g, i) => {{
                let id1 = `p${{currentPhase}}g${{i}}a`, id2 = `p${{currentPhase}}g${{i}}b`;
                // Colisão (Hitbox ajustada pela escala)
                if (!fallenCones.includes(id1) && (Math.hypot(ball.x-g.x1, ball.y-g.y) < 14*getScale(g.y) || Math.hypot(player.x-g.x1, player.y-g.y) < 16*getScale(g.y))) {{ fallenCones.push(id1); score -= 50; }}
                if (!fallenCones.includes(id2) && (Math.hypot(ball.x-g.x2, ball.y-g.y) < 14*getScale(g.y) || Math.hypot(player.x-g.x2, player.y-g.y) < 16*getScale(g.y))) {{ fallenCones.push(id2); score -= 50; }}
            }});
            scoreDisp.innerText = score;

            let gate = currentGates[currentGate];
            if (Math.hypot(ball.x - (gate.x1+gate.x2)/2, ball.y - gate.y) < 25) {{
                currentGate += direction;
                if (currentGate >= currentGates.length && direction === 1) direction = -1, currentGate = currentGates.length-1;
                else if (currentGate < 0 && direction === -1) {{
                    direction = 1; currentGate = 0;
                    if (currentPhase < 2) {{ currentPhase++; phaseDisp.innerText = "2/2"; }}
                    else {{ gameState = 'FINISHED'; alert("TREINO CONCLUÍDO! ID: {st.session_state.player_id} | Score: " + score); }}
                }}
            }}
            render();
            requestAnimationFrame(update);
        }}

        function render() {{
            ctx.fillStyle = '#1e3d1a'; ctx.fillRect(0,0,320,460);
            
            // Gramado (Ponto de Fuga)
            ctx.strokeStyle = "rgba(255,255,255,0.03)";
            for(let i=-100; i<=420; i+=40) {{
                ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i*1.3 - 48, 460); ctx.stroke();
            }}

            let currentGates = phases[currentPhase].gates;
            
            // ORDENAÇÃO DE DESENHO (Z-Order por Y)
            let drawList = [];
            currentGates.forEach((g, i) => {{
                drawList.push({{ type: 'gate', y: g.y, data: g, index: i }});
            }});
            drawList.push({{ type: 'player', y: player.y }});
            drawList.push({{ type: 'ball', y: ball.y }});
            
            drawList.sort((a, b) => a.y - b.y);

            drawList.forEach(obj => {{
                if (obj.type === 'gate') {{
                    drawCone(obj.data.x1, obj.data.y, `p${{currentPhase}}g${{obj.index}}a`);
                    drawCone(obj.data.x2, obj.data.y, `p${{currentPhase}}g${{obj.index}}b`);
                    if (obj.index === currentGate) {{
                        ctx.beginPath(); ctx.moveTo(obj.data.x1, obj.data.y); ctx.lineTo(obj.data.x2, obj.data.y);
                        ctx.strokeStyle = "rgba(0,255,0,0.4)"; ctx.lineWidth = 3*getScale(obj.y); ctx.stroke();
                    }}
                }} else if (obj.type === 'player') {{
                    let s = getScale(player.y);
                    ctx.fillStyle="rgba(0,0,0,0.2)"; ctx.beginPath(); ctx.ellipse(player.x, player.y, 12*s, 5*s, 0, 0, Math.PI*2); ctx.fill();
                    ctx.fillStyle="#ffd700"; ctx.fillRect(player.x-7*s, player.y-25*s, 14*s, 20*s);
                    ctx.fillStyle="#d2b48c"; ctx.beginPath(); ctx.arc(player.x, player.y-32*s, 6*s, 0, Math.PI*2); ctx.fill();
                }} else if (obj.type === 'ball') {{
                    let s = getScale(ball.y);
                    ctx.fillStyle="white"; ctx.beginPath(); ctx.arc(ball.x, ball.y, 6.5*s, 0, Math.PI*2); ctx.fill();
                    ctx.strokeStyle="black"; ctx.lineWidth=1*s; ctx.stroke();
                }}
            }});

            // Joy (Sempre no topo)
            ctx.beginPath(); ctx.arc(joy.x, joy.y, 35, 0, Math.PI*2); ctx.fillStyle='rgba(255,255,255,0.05)'; ctx.fill();
            ctx.beginPath(); ctx.arc(joy.currX, joy.currY, 18, 0, Math.PI*2); ctx.fillStyle='#0f0'; ctx.fill();
        }}

        canvas.addEventListener('pointerdown', e => {{ const r=canvas.getBoundingClientRect(); if(Math.hypot(e.clientX-r.left-joy.x, e.clientY-r.top-joy.y)<50) joy.active=true; }});
        canvas.addEventListener('pointermove', e => {{ if(!joy.active) return; const r=canvas.getBoundingClientRect(); let dx=e.clientX-r.left-joy.x, dy=e.clientY-r.top-joy.y, d=Math.min(Math.hypot(dx,dy),35), a=Math.atan2(dy,dx); joy.currX=joy.x+Math.cos(a)*d; joy.currY=joy.y+Math.sin(a)*d; }});
        canvas.addEventListener('pointerup', () => {{ joy.active=false; joy.currX=joy.x; joy.currY=joy.y; }});
        update();
    </script>
    """

    components.html(game_code, height=530)
    
    if st.button("FINALIZAR SESSÃO"):
        st.session_state.logged_in = False
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("GOAT TV FEDERATION © 2026")
st.sidebar.write("**TECNOLOGIA:** G-PERSPECTIVE 2.5D")
