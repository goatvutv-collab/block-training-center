import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURAÇÃO INSTITUCIONAL - GOAT TV
st.set_page_config(page_title="GOAT TV - CT OFICIAL", layout="centered", initial_sidebar_state="collapsed")

# Sidebar para Identificação do Atleta
st.sidebar.image("https://raw.githubusercontent.com/streamlit/docs/main/public/images/favicon.png", width=50) # Placeholder para logo da Federação
player_id = st.sidebar.text_input("ID DO ATLETA", value="PLAYER_01", help="Insira o ID oficial da Federação")

st.markdown(f"""
    <style>
    .main {{ background-color: #0e1117; }}
    h3 {{ color: #ffd700; text-align: center; font-family: 'Courier New', monospace; margin-top: -30px; text-shadow: 0 0 10px #ffd700; }}
    </style>
    <h3>GOAT TV: TESTE DE APTIDÃO</h3>
""", unsafe_allow_html=True)

# 2. MOTOR DO JOGO: IDA E VOLTA + PLAYER ID
game_code = f"""
<div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
    <div id="hud" style="color: white; font-family: monospace; margin-bottom: 5px; font-size: 11px; background: rgba(0,0,0,0.8); padding: 5px 15px; border-radius: 20px; border: 1px solid #444; width: 300px; display: flex; justify-content: space-between;">
        <span>ID: <b id="pidDisp" style="color: #ffd700;">{player_id}</b></span>
        <span>ETAPA: <b id="phaseName" style="color: #00ff00;">1/2</b></span>
        <span>SCORE: <b id="scoreDisp" style="color: #00ff00;">1000</b></span>
    </div>
    <div style="position: relative;">
        <canvas id="gameCanvas" width="320" height="460" style="background: #1e3d1a; border: 2px solid #555; border-radius: 10px; touch-action: none;"></canvas>
        <div id="countdownOverlay" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #00ff00; font-size: 60px; font-family: sans-serif; font-weight: bold; text-shadow: 0 0 20px black; pointer-events: none;"></div>
    </div>
</div>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const phaseDisp = document.getElementById('phaseName');
    const scoreDisp = document.getElementById('scoreDisp');
    const countOverlay = document.getElementById('countdownOverlay');

    // CONFIGURAÇÕES DO MOTOR
    let player = {{ x: 160, y: 410, speed: 3.6, radius: 10 }};
    let ball = {{ x: 160, y: 385, radius: 6.5 }};
    let score = 1000;
    let currentPhase = 1;
    let currentGate = 0;
    let direction = 1; // 1: Ida, -1: Volta
    let gameState = 'STARTING';
    let countNum = 3;
    let wobble = 0;

    // DEFINIÇÃO DOS CIRCUITOS (Ida e Volta)
    const phases = {{
        1: {{ name: "CIRCUITO U", gates: [
            {{x1: 50, x2: 130, y: 320}}, {{x1: 50, x2: 130, y: 120}}, 
            {{x1: 190, x2: 270, y: 120}}, {{x1: 190, x2: 270, y: 320}}
        ]}},
        2: {{ name: "ZIG-ZAG PRO", gates: [
            {{x1: 40, x2: 100, y: 320}}, {{x1: 220, x2: 280, y: 220}}, 
            {{x1: 40, x2: 100, y: 120}}, {{x1: 220, x2: 280, y: 40}}
        ]}}
    }};

    let fallenCones = [];
    const joy = {{ x: 60, y: 380, baseRadius: 35, stickRadius: 18, currX: 60, currY: 380, active: false }};

    function startCountdown() {{
        gameState = 'STARTING';
        countNum = 3;
        let countInterval = setInterval(() => {{
            if (countNum > 0) {{ countOverlay.innerText = countNum; countNum--; }}
            else if (countNum === 0) {{ countOverlay.innerText = "GO!"; countNum--; }}
            else {{ countOverlay.innerText = ""; gameState = 'PLAYING'; clearInterval(countInterval); }}
        }}, 1000);
    }}
    startCountdown();

    function update() {{
        if (gameState !== 'PLAYING') {{ render(); requestAnimationFrame(update); return; }}

        let vx = 0, vy = 0;
        if (joy.active) {{
            let dx = joy.currX - joy.x, dy = joy.currY - joy.y;
            let dist = Math.hypot(dx, dy);
            if (dist > 0) {{
                vx = (dx / dist) * player.speed;
                vy = (dy / dist) * player.speed;
                player.x += vx; player.y += vy;
                
                wobble += 0.2;
                let targetBallX = player.x + vx * 6 + Math.cos(wobble) * 4;
                let targetBallY = player.y + vy * 6;
                ball.x += (targetBallX - ball.x) * 0.15;
                ball.y += (targetBallY - ball.y) * 0.15;
            }}
        }}

        // FÍSICA DE CONES
        let currentGates = phases[currentPhase].gates;
        currentGates.forEach((g, i) => {{
            let id1 = `p${{currentPhase}}g${{i}}c1`;
            let id2 = `p${{currentPhase}}g${{i}}c2`;
            if (!fallenCones.includes(id1) && (Math.hypot(player.x-g.x1, player.y-g.y) < 18 || Math.hypot(ball.x-g.x1, ball.y-g.y) < 14)) {{ fallenCones.push(id1); score -= 50; }}
            if (!fallenCones.includes(id2) && (Math.hypot(player.x-g.x2, player.y-g.y) < 18 || Math.hypot(ball.x-g.x2, ball.y-g.y) < 14)) {{ fallenCones.push(id2); score -= 50; }}
        }});
        scoreDisp.innerText = score;

        // LÓGICA BATE E VOLTA
        let gate = currentGates[currentGate];
        if (Math.hypot(ball.x - (gate.x1+gate.x2)/2, ball.y - gate.y) < 30) {{
            currentGate += direction;
            
            // Se chegou no fim da Ida, inverte para Volta
            if (currentGate >= currentGates.length && direction === 1) {{
                direction = -1;
                currentGate = currentGates.length - 1;
            }} 
            // Se chegou no fim da Volta, encerra etapa
            else if (currentGate < 0 && direction === -1) {{
                direction = 1;
                currentGate = 0;
                if (currentPhase < 2) {{
                    currentPhase++;
                    phaseDisp.innerText = currentPhase + "/2";
                    startCountdown();
                }} else {{
                    gameState = 'FINISHED';
                    alert("🎖️ RELATÓRIO FINAL GOAT TV\\nID: {player_id}\\nScore de Equilíbrio: " + score);
                    location.reload();
                }}
            }}
        }}

        player.x = Math.max(10, Math.min(310, player.x));
        player.y = Math.max(10, Math.min(450, player.y));
        render();
        requestAnimationFrame(update);
    }}

    function render() {{
        ctx.fillStyle = '#1e3d1a'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        let currentGates = phases[currentPhase].gates;
        currentGates.forEach((g, i) => {{
            let s = g.y / 460 + 0.5;
            let id1 = `p${{currentPhase}}g${{i}}c1`, id2 = `p${{currentPhase}}g${{i}}c2`;
            [ {{x: g.x1, id: id1}}, {{x: g.x2, id: id2}} ].forEach(c => {{
                if (fallenCones.includes(c.id)) {{
                    ctx.fillStyle = "rgba(150, 75, 0, 0.4)"; ctx.beginPath(); ctx.ellipse(c.x, g.y, 12*s, 3*s, 0, 0, Math.PI*2); ctx.fill();
                }} else {{
                    ctx.fillStyle = "#ff6600"; ctx.beginPath(); ctx.moveTo(c.x-8*s, g.y); ctx.lineTo(c.x+8*s, g.y); ctx.lineTo(c.x, g.y-22*s); ctx.fill();
                }}
            }});
            if (i === currentGate) {{
                ctx.beginPath(); ctx.moveTo(g.x1, g.y); ctx.lineTo(g.x2, g.y);
                ctx.strokeStyle = "rgba(0, 255, 0, 0.6)"; ctx.lineWidth = 4; ctx.stroke();
            }}
        }});
        let s = player.y / 460 + 0.5;
        ctx.fillStyle = "rgba(0,0,0,0.2)"; ctx.beginPath(); ctx.ellipse(player.x, player.y, 12*s, 5*s, 0, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = "white"; ctx.beginPath(); ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = "#ffd700"; ctx.fillRect(player.x-7*s, player.y-25*s, 14*s, 20*s);
        ctx.fillStyle = "#d2b48c"; ctx.beginPath(); ctx.arc(player.x, player.y-32*s, 6*s, 0, Math.PI*2); ctx.fill();
        // Joy
        ctx.beginPath(); ctx.arc(joy.x, joy.y, joy.baseRadius, 0, Math.PI*2); ctx.fillStyle = 'rgba(255,255,255,0.05)'; ctx.fill();
        ctx.beginPath(); ctx.arc(joy.currX, joy.currY, joy.stickRadius, 0, Math.PI*2); ctx.fillStyle = '#00ff00'; ctx.fill();
    }}

    canvas.addEventListener('pointerdown', e => {{ const r = canvas.getBoundingClientRect(); if (Math.hypot((e.clientX-r.left)-joy.x, (e.clientY-r.top)-joy.y) < 50) joy.active = true; }});
    canvas.addEventListener('pointermove', e => {{
        if (!joy.active) return;
        const r = canvas.getBoundingClientRect();
        let dx = (e.clientX-r.left)-joy.x, dy = (e.clientY-r.top)-joy.y;
        let d = Math.min(Math.hypot(dx,dy), joy.baseRadius), a = Math.atan2(dy,dx);
        joy.currX = joy.x + Math.cos(a)*d; joy.currY = joy.y + Math.sin(a)*d;
    }});
    canvas.addEventListener('pointerup', () => {{ joy.active=false; joy.currX=joy.x; joy.currY=joy.y; }});
    update();
</script>
"""

components.html(game_code, height=530)

st.sidebar.markdown("---")
st.sidebar.write(f"**Atleta Conectado:** {player_id}")
st.sidebar.info("Modo de Bate-Volta Ativo. O circuito exige ida e retorno para validação.")
