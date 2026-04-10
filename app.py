import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURAÇÃO DO DESAFIO COM FÍSICA
st.set_page_config(page_title="GOAT TV - CIRCUITO FÍSICO", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h3 { color: #00ff00; text-align: center; font-family: sans-serif; margin-top: -30px; text-shadow: 0 0 10px #00ff00; }
    </style>
    <h3>🏆 TESTE DE PRECISÃO: DRIBLE LIMPO</h3>
""", unsafe_allow_html=True)

# 2. MOTOR DO JOGO COM FÍSICA DE CONES E SCORE
game_code = """
<div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
    <div id="hud" style="color: white; font-family: monospace; margin-bottom: 5px; font-size: 13px; background: rgba(0,0,0,0.6); padding: 5px 15px; border-radius: 20px; display: flex; gap: 15px;">
        <span>VOLTAS: <b id="lapCount" style="color: #00ff00;">0/5</b></span>
        <span>TEMPO: <b id="timer" style="color: #ff4444;">60.0s</b></span>
        <span>SCORE: <b id="scoreDisp" style="color: #ffd700;">1000</b></span>
    </div>
    <div style="position: relative;">
        <canvas id="gameCanvas" width="320" height="450" style="background: #244d20; border: 2px solid #555; border-radius: 10px; touch-action: none;"></canvas>
        <div id="countdownOverlay" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #00ff00; font-size: 80px; font-family: sans-serif; font-weight: bold; text-shadow: 0 0 20px black; pointer-events: none;"></div>
    </div>
</div>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const lapDisp = document.getElementById('lapCount');
    const timeDisp = document.getElementById('timer');
    const scoreDisp = document.getElementById('scoreDisp');
    const countOverlay = document.getElementById('countdownOverlay');

    let player = { x: 160, y: 400, speed: 3.2, radius: 10 };
    let score = 1000;
    let laps = 0;
    let timeLeft = 60.0;
    let currentGate = 0;
    let gameState = 'STARTING';
    let countNum = 3;

    // Cones com Propriedade de Física (isDown)
    const gates = [
        { x1: 50, x2: 130, y: 320, cone1Down: false, cone2Down: false },
        { x1: 50, x2: 130, y: 120, cone1Down: false, cone2Down: false },
        { x1: 190, x2: 270, y: 120, cone1Down: false, cone2Down: false },
        { x1: 190, x2: 270, y: 320, cone1Down: false, cone2Down: false }
    ];

    const joy = { x: 60, y: 380, baseRadius: 35, stickRadius: 18, currX: 60, currY: 380, active: false };

    // Countdown
    let countInterval = setInterval(() => {
        if (countNum > 0) { countOverlay.innerText = countNum; countNum--; }
        else if (countNum === 0) { countOverlay.innerText = "GO!"; countNum--; }
        else { countOverlay.innerText = ""; gameState = 'PLAYING'; clearInterval(countInterval); }
    }, 1000);

    function drawCone(x, y, s, isDown) {
        if (isDown) {
            // Cone Derrubado (Desenho achatado no chão)
            ctx.fillStyle = "rgba(100, 100, 100, 0.6)"; // Cor de "objeto caído"
            ctx.beginPath();
            ctx.ellipse(x, y, 15*s, 5*s, Math.PI/4, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = "#cc5200"; // Laranja escuro
            ctx.fillRect(x-10*s, y-2, 20*s, 4*s);
        } else {
            // Cone de Pé
            ctx.fillStyle = "#ff6600";
            ctx.beginPath();
            ctx.moveTo(x - 8*s, y); ctx.lineTo(x + 8*s, y);
            ctx.lineTo(x, y - 22*s); ctx.fill();
            ctx.fillStyle = "#333"; ctx.fillRect(x - 9*s, y - 2, 18*s, 3);
        }
    }

    function update() {
        if (gameState !== 'PLAYING') { render(); requestAnimationFrame(update); return; }

        if (joy.active) {
            let dx = joy.currX - joy.x; let dy = joy.currY - joy.y;
            let dist = Math.hypot(dx, dy);
            if (dist > 0) {
                player.x += (dx / dist) * player.speed;
                player.y += (dy / dist) * player.speed;
            }
        }

        // FÍSICA DE COLISÃO COM CONES
        gates.forEach(g => {
            // Checa cone 1 do portão
            if (!g.cone1Down && Math.hypot(player.x - g.x1, player.y - g.y) < 18) {
                g.cone1Down = true; score -= 100;
            }
            // Checa cone 2 do portão
            if (!g.cone2Down && Math.hypot(player.x - g.x2, player.y - g.y) < 18) {
                g.cone2Down = true; score -= 100;
            }
        });
        scoreDisp.innerText = Math.max(0, score);

        // Lógica de Portão
        let gate = gates[currentGate];
        let midX = (gate.x1 + gate.x2) / 2;
        if (Math.hypot(player.x - midX, player.y - gate.y) < 35) {
            currentGate++;
            if (currentGate >= gates.length) {
                currentGate = 0; laps++;
                lapDisp.innerText = laps + "/5";
                if (laps >= 5) finish('WIN');
            }
        }

        timeLeft -= 1/60;
        timeDisp.innerText = Math.max(0, timeLeft).toFixed(1) + "s";
        if (timeLeft <= 0) finish('LOSE');

        render();
        requestAnimationFrame(update);
    }

    function render() {
        ctx.fillStyle = '#244d20';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        gates.forEach((g, i) => {
            let s = g.y / 450 + 0.5;
            drawCone(g.x1, g.y, s, g.cone1Down);
            drawCone(g.x2, g.y, s, g.cone2Down);
            
            if (i === currentGate) {
                ctx.beginPath(); ctx.moveTo(g.x1, g.y); ctx.lineTo(g.x2, g.y);
                ctx.strokeStyle = "#00ff00"; ctx.lineWidth = 3;
                ctx.setLineDash([5, 3]); ctx.stroke(); ctx.setLineDash([]);
            }
        });

        // Player Aysher
        let pScale = player.y / 450 + 0.5;
        ctx.fillStyle = 'rgba(0,0,0,0.2)';
        ctx.beginPath(); ctx.ellipse(player.x, player.y, 12*pScale, 5*pScale, 0, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = '#ffd700'; ctx.fillRect(player.x-6*pScale, player.y-25*pScale, 12*pScale, 18*pScale);
        ctx.fillStyle = '#d2b48c'; ctx.beginPath(); ctx.arc(player.x, player.y-32*pScale, 5*pScale, 0, Math.PI*2); ctx.fill();

        // Analog
        ctx.beginPath(); ctx.arc(joy.x, joy.y, joy.baseRadius, 0, Math.PI*2);
        ctx.fillStyle = 'rgba(255,255,255,0.1)'; ctx.fill();
        ctx.beginPath(); ctx.arc(joy.currX, joy.currY, joy.stickRadius, 0, Math.PI*2);
        ctx.fillStyle = '#00ff00'; ctx.fill();
    }

    function finish(type) {
        gameState = 'FINISHED';
        if (type === 'WIN') {
            let finalNote = score >= 800 ? "9.0 (ELITE)" : score >= 500 ? "7.5 (MÉDIO)" : "6.0 (BASE)";
            alert("TREINO CONCLUÍDO!\\nScore Final: " + score + "\\nNota: " + finalNote);
        } else {
            alert("TEMPO ESGOTADO! O drible precisa ser mais ágil.");
        }
        location.reload();
    }

    // Touch Handlers
    canvas.addEventListener('pointerdown', e => {
        const rect = canvas.getBoundingClientRect();
        let tx = e.clientX - rect.left; let ty = e.clientY - rect.top;
        if (Math.hypot(tx-joy.x, ty-joy.y) < joy.baseRadius*1.5) joy.active = true;
    });
    canvas.addEventListener('pointermove', e => {
        if (!joy.active) return;
        const rect = canvas.getBoundingClientRect();
        let dx = (e.clientX - rect.left) - joy.x;
        let dy = (e.clientY - rect.top) - joy.y;
        let dist = Math.hypot(dx, dy);
        let moveDist = Math.min(dist, joy.baseRadius);
        let ang = Math.atan2(dy, dx);
        joy.currX = joy.x + Math.cos(ang) * moveDist;
        joy.currY = joy.y + Math.sin(ang) * moveDist;
    });
    canvas.addEventListener('pointerup', () => { joy.active = false; joy.currX = joy.x; joy.currY = joy.y; });

    update();
</script>
"""

components.html(game_code, height=530)

# Sidebar
st.sidebar.markdown("### 🏟️ REGRAS DO TESTE")
st.sidebar.write("Pontuação Inicial: **1000**")
st.sidebar.write("Derrubar Cone: **-100 pts**")
st.sidebar.markdown("---")
st.sidebar.info("Nota 9.0 requer terminar as 5 voltas com pelo menos 800 pontos. Drible limpo é a chave!")
