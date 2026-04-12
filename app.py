import streamlit as st
import streamlit.components.v1 as components
import json
import os
import re

# 1. CONFIGURAÇÃO INSTITUCIONAL - GOAT TV
st.set_page_config(page_title="GOAT TV - CT PERSPECTIVA", layout="centered", initial_sidebar_state="collapsed")

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

def aplicar_evolucao(player_id, tipo, score):
    data = load_data()
    if player_id not in data: data[player_id] = {"stats": {}, "history": []}
    p = data[player_id].get("stats", {})
    if score > 500:
        for s in TREINOS_LOGIC[tipo]["sobe"]: p[s] = min(p.get(s, 70) + 1.8, 95)
        for d in TREINOS_LOGIC[tipo]["desce"]: p[d] = max(p.get(d, 70) - 1.4, 50)
    data[player_id]["stats"] = p
    save_data(data)

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

# --- TELA 2: CAMPO DE TREINAMENTO ---
else:
    st.markdown(f"### 🏟️ CT GOAT TV | ATLETA: {st.session_state.player_id}")
    
    # Configuração de fases (Adicionado Fase 3 com Marcadores no Drible)
    fases_config = {
        "DRIBLE": """{
            1: {gates:[{x1:60,x2:120,y:320},{x1:60,x2:120,y:150},{x1:200,x2:260,y:150},{x1:200,x2:260,y:320}], enemies:[]},
            2: {gates:[{x1:40,x2:100,y:320},{x1:130,x2:190,y:200},{x1:220,x2:280,y:80}], enemies:[]},
            3: {gates:[{x1:130,x2:190,y:60}], enemies:[
                {x:160, y:280, range:80, speed:2.5, dir:1},
                {x:160, y:150, range:110, speed:3.5, dir:-1}
            ]}
        }""",
        "PASSE": "{1: {gates:[{x1:130,x2:190,y:100}], enemies:[]}, 2: {gates:[{x1:130,x2:190,y:80}], enemies:[]}, 3: {gates:[], enemies:[]}}",
        "FINALIZACAO": "{1: {gates:[{x1:100,x2:220,y:120}], enemies:[]}, 2: {gates:[{x1:80,x2:240,y:100}], enemies:[]}, 3: {gates:[], enemies:[]}}",
        "DEFESA": "{1: {gates:[{x1:40,x2:280,y:230}], enemies:[]}, 2: {gates:[], enemies:[]}, 3: {gates:[], enemies:[]}}"
    }

    game_code = f"""
    <div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
        <div id="hud" style="color: white; font-family: monospace; margin-bottom: 8px; font-size: 11px; background: rgba(0,0,0,0.9); padding: 5px 15px; border-radius: 20px; border: 1px solid #ffd700; width: 300px; display: flex; justify-content: space-between;">
            <span>ID: <b style="color: #ffd700;">{st.session_state.player_id}</b></span>
            <span>ETAPA: <b id="phaseDisp" style="color: #0f0;">1/3</b></span>
            <span>SCORE: <b id="scoreDisp" style="color: #0f0;">1000</b></span>
        </div>
        <canvas id="gameCanvas" width="320" height="460" style="background: #1e3d1a; border: 2px solid #555; border-radius: 10px; touch-action: none;"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreDisp = document.getElementById('scoreDisp');
        const phaseDisp = document.getElementById('phaseDisp');

        let player = {{ x: 160, y: 410, speed: 4.2 }};
        let ball = {{ x: 160, y: 385 }};
        let score = 1000;
        let currentPhase = 1;
        let currentGate = 0;
        let direction = 1; 
        let gameState = 'PLAYING';
        let fallenCones = [];

        const phases = {fases_config[st.session_state.treino_selecionado]};

        const joy = {{ x: 60, y: 385, baseRadius: 35, currX: 60, currY: 385, active: false }};

        function getScale(y) {{ return (y / 460) * 0.55 + 0.45; }}

        function drawCone(x, y, id) {{
            let s = getScale(y);
            let isDown = fallenCones.includes(id);
            if (isDown) {{
                ctx.fillStyle = "rgba(0,0,0,0.2)";
                ctx.beginPath(); ctx.ellipse(x, y, 12*s, 4*s, 0, 0, Math.PI*2); ctx.fill();
            }} else {{
                ctx.fillStyle = "#ff6600";
                ctx.beginPath(); ctx.moveTo(x-8*s, y); ctx.lineTo(x+8*s, y); ctx.lineTo(x, y-22*s); ctx.fill();
            }}
        }}

        function drawEnemy(e) {{
            let s = getScale(e.y);
            // Sombra
            ctx.fillStyle="rgba(0,0,0,0.3)"; ctx.beginPath(); ctx.ellipse(e.x, e.y, 14*s, 6*s, 0, 0, Math.PI*2); ctx.fill();
            // Corpo (Uniforme Vermelho de treino)
            ctx.fillStyle="#ff3333"; ctx.fillRect(e.x-9*s, e.y-28*s, 18*s, 22*s);
            // Cabeça
            ctx.fillStyle="#d2b48c"; ctx.beginPath(); ctx.arc(e.x, e.y-35*s, 7*s, 0, Math.PI*2); ctx.fill();
        }}

        function update() {{
            if (gameState !== 'PLAYING') return;

            if (joy.active) {{
                let dx = joy.currX - joy.x, dy = joy.currY - joy.y, d = Math.hypot(dx, dy);
                if (d > 0) {{
                    let vx = (dx/d)*player.speed, vy = (dy/d)*player.speed;
                    player.x += vx; player.y += vy;
                    ball.x += (player.x + vx*6 - ball.x) * 0.25;
                    ball.y += (player.y + vy*6 - ball.y) * 0.25;
                }}
            }}

            // Movimentação dos Inimigos (Marcação Linear)
            let phaseData = phases[currentPhase];
            if(phaseData.enemies) {{
                phaseData.enemies.forEach(e => {{
                    e.x += e.speed * e.dir;
                    if (Math.abs(e.x - 160) > e.range/2) e.dir *= -1;
                    
                    // Colisão com Marcador (Perca de Score alta)
                    if (Math.hypot(player.x - e.x, player.y - e.y) < 20*getScale(e.y)) {{
                        score -= 2; // Penalidade contínua por contato
                    }}
                }});
            }}

            let currentGates = phaseData.gates;
            currentGates.forEach((g, i) => {{
                let id1 = `p${{currentPhase}}g${{i}}a`, id2 = `p${{currentPhase}}g${{i}}b`;
                let s = getScale(g.y);
                if (!fallenCones.includes(id1) && Math.hypot(player.x-g.x1, player.y-g.y) < 15*s) {{ fallenCones.push(id1); score -= 50; }}
                if (!fallenCones.includes(id2) && Math.hypot(player.x-g.x2, player.y-g.y) < 15*s) {{ fallenCones.push(id2); score -= 50; }}
            }});
            scoreDisp.innerText = Math.floor(score);

            if (currentGates.length > 0) {{
                let gate = currentGates[currentGate];
                if (Math.hypot(ball.x - (gate.x1+gate.x2)/2, ball.y - gate.y) < 30) {{
                    currentGate += direction;
                    if (currentGate >= currentGates.length) {{
                        if (currentPhase < 3) {{ 
                            currentPhase++; 
                            currentGate = 0; 
                            phaseDisp.innerText = currentPhase + "/3";
                        }} else {{ 
                            gameState = 'FINISHED'; 
                            alert("TREINO CONCLUÍDO! SCORE: " + Math.floor(score)); 
                        }}
                    }}
                }}
            }}
            
            render();
            requestAnimationFrame(update);
        }}

        function render() {{
            ctx.fillStyle = '#1e3d1a'; ctx.fillRect(0,0,320,460);
            
            // Gramado (Linhas de profundidade)
            ctx.strokeStyle = "rgba(255,255,255,0.05)";
            for(let i=-50; i<=370; i+=40) {{
                ctx.beginPath(); ctx.moveTo(160, -50); ctx.lineTo(i*1.5 - 80, 460); ctx.stroke();
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
                    drawCone(obj.data.x1, obj.data.y, `p${{currentPhase}}g${{obj.index}}a`);
                    drawCone(obj.data.x2, obj.data.y, `p${{currentPhase}}g${{obj.index}}b`);
                    if (obj.index === currentGate) {{
                        ctx.strokeStyle = "rgba(0,255,0,0.5)"; ctx.setLineDash([5, 5]);
                        ctx.beginPath(); ctx.moveTo(obj.data.x1, obj.data.y); ctx.lineTo(obj.data.x2, obj.data.y); ctx.stroke();
                        ctx.setLineDash([]);
                    }}
                }} else if (obj.type === 'enemy') {{
                    drawEnemy(obj.data);
                }} else if (obj.type === 'player') {{
                    ctx.fillStyle="rgba(0,0,0,0.3)"; ctx.beginPath(); ctx.ellipse(player.x, player.y, 12*s, 5*s, 0, 0, Math.PI*2); ctx.fill();
                    ctx.fillStyle="#ffd700"; ctx.fillRect(player.x-8*s, player.y-28*s, 16*s, 22*s);
                    ctx.fillStyle="#d2b48c"; ctx.beginPath(); ctx.arc(player.x, player.y-35*s, 7*s, 0, Math.PI*2); ctx.fill();
                }} else if (obj.type === 'ball') {{
                    ctx.fillStyle="white"; ctx.beginPath(); ctx.arc(ball.x, ball.y, 6*s, 0, Math.PI*2); ctx.fill();
                    ctx.strokeStyle="#000"; ctx.lineWidth=1; ctx.stroke();
                }}
            }});

            // Joystick
            ctx.beginPath(); ctx.arc(joy.x, joy.y, 35, 0, Math.PI*2); ctx.fillStyle='rgba(255,255,255,0.1)'; ctx.fill();
            ctx.beginPath(); ctx.arc(joy.currX, joy.currY, 15, 0, Math.PI*2); ctx.fillStyle='#0f0'; ctx.fill();
        }}

        canvas.addEventListener('pointerdown', e => {{ const r=canvas.getBoundingClientRect(); if(Math.hypot(e.clientX-r.left-joy.x, e.clientY-r.top-joy.y)<50) joy.active=true; }});
        canvas.addEventListener('pointermove', e => {{ if(!joy.active) return; const r=canvas.getBoundingClientRect(); let dx=e.clientX-r.left-joy.x, dy=e.clientY-r.top-joy.y, d=Math.min(Math.hypot(dx,dy),35), a=Math.atan2(dy,dx); joy.currX=joy.x+Math.cos(a)*d; joy.currY=joy.y+Math.sin(a)*d; }});
        canvas.addEventListener('pointerup', () => {{ joy.active=false; joy.currX=joy.x; joy.currY=joy.y; }});
        update();
    </script>
    """

    components.html(game_code, height=540)
    
    if st.button("FINALIZAR E SALVAR EVOLUÇÃO", use_container_width=True):
        aplicar_evolucao(st.session_state.player_id, st.session_state.treino_selecionado, 1000)
        st.success(f"Estatísticas atualizadas para {st.session_state.player_id}!")
        st.session_state.logged_in = False
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("**GOAT TV FEDERATION**")
st.sidebar.caption("G-PERSPECTIVE 2.5D | Módulo de Marcação")
