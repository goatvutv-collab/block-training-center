import streamlit as st
import streamlit.components.v1 as components
import json
import os
import re

# 1. CONFIGURAÇÃO INSTITUCIONAL - GOAT TV
st.set_page_config(page_title="GOAT TV - PORTAL CT", layout="centered", initial_sidebar_state="collapsed")

# --- SISTEMA DE REGISTRO (GOAT REGISTRY) ---
DB_FILE = "goat_players.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def is_valid_id(pid):
    # Apenas letras e números (conforme solicitado pelo Comissário)
    return bool(re.match("^[a-zA-Z0-9]*$", pid))

# Gerenciamento de Sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.player_id = ""

# --- TELA 1: PORTAL DE ENTRADA (SEM TRAVA TEMPORAL) ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center; color: #ffd700;'>GOAT TV: PORTAL DE ACESSO</h2>", unsafe_allow_html=True)
    st.write("---")
    
    pid_input = st.text_input("DIGITE SEU ID DE ATLETA:", "").strip().upper()
    
    if st.button("INICIAR TREINAMENTO"):
        if not pid_input:
            st.error("Por favor, insira um ID para prosseguir.")
        elif not is_valid_id(pid_input):
            st.error("ID inválido! Use apenas letras e números, sem espaços.")
        else:
            # Registro simples no banco de dados
            data = load_data()
            if pid_input not in data:
                data[pid_input] = {"best_score": 0}
                save_data(data)
            
            st.session_state.logged_in = True
            st.session_state.player_id = pid_input
            st.rerun()

# --- TELA 2: CAMPO DE TREINAMENTO (POCKET CONSOLE) ---
else:
    st.markdown(f"### 🏟️ ATLETA EM CAMPO: {st.session_state.player_id}")
    
    # Motor de Jogo: Ida e Volta, 2 Estágios (U e Zig-Zag)
    game_code = f"""
    <div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
        <div id="hud" style="color: white; font-family: monospace; margin-bottom: 5px; font-size: 11px; background: rgba(0,0,0,0.8); padding: 5px 15px; border-radius: 20px; border: 1px solid #444; width: 310px; display: flex; justify-content: space-between;">
            <span>ID: <b style="color: #ffd700;">{st.session_state.player_id}</b></span>
            <span>FASE: <b id="phaseDisp" style="color: #0f0;">1/2</b></span>
            <span>SCORE: <b id="scoreDisp" style="color: #0f0;">1000</b></span>
        </div>
        <canvas id="gameCanvas" width="320" height="460" style="background: #1e3d1a; border: 2px solid #555; border-radius: 10px; touch-action: none;"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreDisp = document.getElementById('scoreDisp');
        const phaseDisp = document.getElementById('phaseDisp');

        let player = {{ x: 160, y: 410, speed: 3.5, radius: 10 }};
        let ball = {{ x: 160, y: 385, radius: 6.5 }};
        let score = 1000;
        let currentPhase = 1;
        let currentGate = 0;
        let direction = 1; // 1: Ida, -1: Volta
        let gameState = 'PLAYING';
        let wobble = 0;

        const phases = {{
            1: {{ gates: [{{x1: 50, x2: 130, y: 320}}, {{x1: 50, x2: 130, y: 120}}, {{x1: 190, x2: 270, y: 120}}, {{x1: 190, x2: 270, y: 320}}] }},
            2: {{ gates: [{{x1: 40, x2: 100, y: 320}}, {{x1: 220, x2: 280, y: 220}}, {{x1: 40, x2: 100, y: 120}}, {{x1: 220, x2: 280, y: 40}}] }}
        }};

        let fallenCones = [];
        const joy = {{ x: 60, y: 380, baseRadius: 35, stickRadius: 18, currX: 60, currY: 380, active: false }};

        function lerp(start, end, amt) {{ return (1 - amt) * start + amt * end; }}

        function update() {{
            if (gameState !== 'PLAYING') return;

            if (joy.active) {{
                let dx = joy.currX - joy.x, dy = joy.currY - joy.y, d = Math.hypot(dx, dy);
                if (d > 0) {{
                    let vx = (dx/d)*player.speed, vy = (dy/d)*player.speed;
                    player.x += vx; player.y += vy;
                    wobble += 0.2;
                    let targetX = player.x + vx*6 + Math.cos(wobble)*4;
                    let targetY = player.y + vy*6;
                    ball.x = lerp(ball.x, targetX, 0.15);
                    ball.y = lerp(ball.y, targetY, 0.15);
                }}
            }}

            // FÍSICA DE CONES (Derrubar)
            let currentGates = phases[currentPhase].gates;
            currentGates.forEach((g, i) => {{
                let id1 = `p${{currentPhase}}g${{i}}a`, id2 = `p${{currentPhase}}g${{i}}b`;
                if (!fallenCones.includes(id1) && Math.hypot(ball.x-g.x1, ball.y-g.y) < 15) {{ fallenCones.push(id1); score -= 50; }}
                if (!fallenCones.includes(id2) && Math.hypot(ball.x-g.x2, ball.y-g.y) < 15) {{ fallenCones.push(id2); score -= 50; }}
            }});
            scoreDisp.innerText = score;

            // LÓGICA BATE E VOLTA
            let gate = currentGates[currentGate];
            if (Math.hypot(ball.x - (gate.x1+gate.x2)/2, ball.y - gate.y) < 30) {{
                currentGate += direction;
                if (currentGate >= currentGates.length && direction === 1) {{ direction = -1; currentGate = currentGates.length - 1; }}
                else if (currentGate < 0 && direction === -1) {{
                    direction = 1; currentGate = 0;
                    if (currentPhase < 2) {{ currentPhase++; phaseDisp.innerText = currentPhase + "/2"; }}
                    else {{ gameState = 'FINISHED'; alert("TREINO CONCLUÍDO!\\nID: {st.session_state.player_id}\\nScore Final: " + score); }}
                }}
            }}
            render();
            requestAnimationFrame(update);
        }}

        function render() {{
            ctx.fillStyle = '#1e3d1a'; ctx.fillRect(0,0,320,460);
            let currentGates = phases[currentPhase].gates;
            currentGates.forEach((g, i) => {{
                let s = g.y/460+0.5;
                [g.x1, g.x2].forEach((x, idx) => {{
                    let id = idx===0 ? `p${{currentPhase}}g${{i}}a` : `p${{currentPhase}}g${{i}}b`;
                    ctx.fillStyle = fallenCones.includes(id) ? "rgba(100,50,0,0.4)" : "#ff6600";
                    ctx.beginPath(); ctx.moveTo(x-8*s, g.y); ctx.lineTo(x+8*s, g.y); ctx.lineTo(x, g.y-22*s); ctx.fill();
                }});
                if (i === currentGate) {{ ctx.beginPath(); ctx.moveTo(g.x1,g.y); ctx.lineTo(g.x2,g.y); ctx.strokeStyle="#0f0"; ctx.lineWidth=3; ctx.stroke(); }}
            }});
            ctx.fillStyle="white"; ctx.beginPath(); ctx.arc(ball.x, ball.y, 6, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle="#ffd700"; ctx.fillRect(player.x-7, player.y-25, 14, 20); // Avatar Amarelo
            // Joystick
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
    
    if st.button("SAIR E VOLTAR AO PORTAL"):
        st.session_state.logged_in = False
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("GOAT TV FEDERATION © 2026")
st.sidebar.write("**MODO:** DESENVOLVIMENTO (Acesso Livre)")
