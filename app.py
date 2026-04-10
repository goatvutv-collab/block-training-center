import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURAÇÃO CT MOBILE - MÓDULO DE PRECISÃO
st.set_page_config(page_title="GOAT TV - CT DRIBLE", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h3 { color: #00ff00; text-align: center; font-family: sans-serif; margin-top: -30px; text-shadow: 0 0 10px #00ff00; }
    </style>
    <h3>⚽ CT GOAT: CONDUÇÃO DE PRECISÃO</h3>
""", unsafe_allow_html=True)

# 2. MOTOR DO JOGO COM GINGA E HITBOX DUPLA
game_code = """
<div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
    <div id="hud" style="color: white; font-family: monospace; margin-bottom: 5px; font-size: 13px; background: rgba(0,0,0,0.6); padding: 5px 15px; border-radius: 20px; display: flex; gap: 15px;">
        <span>VOLTAS: <b id="lapCount" style="color: #00ff00;">0/5</b></span>
        <span>SCORE: <b id="scoreDisp" style="color: #ffd700;">1000</b></span>
    </div>
    <div style="position: relative;">
        <canvas id="gameCanvas" width="320" height="460" style="background: #244d20; border: 2px solid #555; border-radius: 10px; touch-action: none;"></canvas>
        <div id="countdownOverlay" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #00ff00; font-size: 80px; font-family: sans-serif; font-weight: bold; text-shadow: 0 0 20px black; pointer-events: none;"></div>
    </div>
</div>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const lapDisp = document.getElementById('lapCount');
    const scoreDisp = document.getElementById('scoreDisp');
    const countOverlay = document.getElementById('countdownOverlay');

    // ENTIDADES
    let player = { x: 160, y: 400, speed: 3.4, radius: 11 };
    let ball = { x: 160, y: 375, radius: 6.5 };
    
    let score = 1000;
    let laps = 0;
    let currentGate = 0;
    let gameState = 'STARTING';
    let countNum = 3;
    let wobble = 0; // Efeito de ginga da bola

    const gates = [
        { x1: 50, x2: 130, y: 300, c1Down: false, c2Down: false },
        { x1: 50, x2: 130, y: 120, c1Down: false, c2Down: false },
        { x1: 190, x2: 270, y: 120, c1Down: false, c2Down: false },
        { x1: 190, x2: 270, y: 300, c1Down: false, c2Down: false }
    ];

    const joy = { x: 60, y: 380, baseRadius: 35, stickRadius: 18, currX: 60, currY: 380, active: false };

    // COUNTDOWN
    let countInterval = setInterval(() => {
        if (countNum > 0) { countOverlay.innerText = countNum; countNum--; }
        else if (countNum === 0) { countOverlay.innerText = "GO!"; countNum--; }
        else { countOverlay.innerText = ""; gameState = 'PLAYING'; clearInterval(countInterval); }
    }, 1000);

    function lerp(start, end, amt) { return (1 - amt) * start + amt * end; }

    function drawCone(x, y, isDown) {
        let s = y / 460 + 0.5;
        if (isDown) {
            ctx.fillStyle = "rgba(100, 50, 0, 0.4)";
            ctx.beginPath(); ctx.ellipse(x, y, 14*s, 4*s, 0, 0, Math.PI*2); ctx.fill();
        } else {
            ctx.fillStyle = "#ff6600";
            ctx.beginPath(); ctx.moveTo(x-8*s, y); ctx.lineTo(x+8*s, y); ctx.lineTo(x, y-22*s); ctx.fill();
            ctx.fillStyle = "#333"; ctx.fillRect(x-9*s, y-1, 18*s, 3);
        }
    }

    function update() {
        if (gameState !== 'PLAYING') { render(); requestAnimationFrame(update); return; }

        let vx = 0, vy = 0;
        if (joy.active) {
            let dx = joy.currX - joy.x, dy = joy.currY - joy.y;
            let dist = Math.hypot(dx, dy);
            if (dist > 0) {
                vx = (dx / dist) * player.speed;
                vy = (dy / dist) * player.speed;
                player.x += vx; player.y += vy;
                
                // GINGA DA BOLA: Oscila conforme o movimento
                wobble += 0.15;
                let lateralWobble = Math.sin(wobble) * 6; // Desvio lateral de 6px
                
                // A bola segue a direção do movimento com a ginga lateral
                let targetBallX = player.x + vx * 6 + Math.cos(Math.atan2(vy, vx) + Math.PI/2) * lateralWobble;
                let targetBallY = player.y + vy * 6 + Math.sin(Math.atan2(vy, vx) + Math.PI/2) * lateralWobble;
                
                ball.x = lerp(ball.x, targetBallX, 0.12);
                ball.y = lerp(ball.y, targetBallY, 0.12);
            }
        }

        // COLISÃO DUPLA (JOGADOR OU BOLA)
        gates.forEach(g => {
            let hitC1 = Math.hypot(player.x - g.x1, player.y - g.y) < 18 || Math.hypot(ball.x - g.x1, ball.y - g.y) < 14;
            let hitC2 = Math.hypot(player.x - g.x2, player.y - g.y) < 18 || Math.hypot(ball.x - g.x2, ball.y - g.y) < 14;
            
            if (!g.c1Down && hitC1) { g.c1Down = true; score -= 100; }
            if (!g.c2Down && hitC2) { g.c2Down = true; score -= 100; }
        });
        scoreDisp.innerText = Math.max(0, score);

        // PORTÃO
        let gate = gates[currentGate];
        if (Math.hypot(ball.x - (gate.x1+gate.x2)/2, ball.y - gate.y) < 30) {
            currentGate++;
            if (currentGate >= gates.length) {
                currentGate = 0; laps++;
                lapDisp.innerText = laps + "/5";
                if (laps >= 5) { alert("TREINO FINALIZADO!\\nNota Condução: " + (score/100).toFixed(1)); location.reload(); }
            }
        }

        player.x = Math.max(15, Math.min(305, player.x));
        player.y = Math.max(15, Math.min(445, player.y));
        render();
        requestAnimationFrame(update);
    }

    function render() {
        ctx.fillStyle = '#244d20'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        gates.forEach((g, i) => {
            drawCone(g.x1, g.y, g.c1Down);
            drawCone(g.x2, g.y, g.c2Down);
            if (i === currentGate) {
                ctx.beginPath(); ctx.moveTo(g.x1, g.y); ctx.lineTo(g.x2, g.y);
                ctx.strokeStyle = "rgba(0, 255, 0, 0.4)"; ctx.lineWidth = 3;
                ctx.setLineDash([5, 3]); ctx.stroke(); ctx.setLineDash([]);
            }
        });

        // Sombras
        let s = player.y / 460 + 0.5;
        ctx.fillStyle = "rgba(0,0,0,0.2)"; 
        ctx.beginPath(); ctx.ellipse(player.x, player.y, 12*s, 5*s, 0, 0, Math.PI*2); ctx.fill();

        // Bola (Visível acima da sombra)
        ctx.fillStyle = "white"; ctx.beginPath(); ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = "black"; ctx.lineWidth = 1; ctx.stroke();

        // Boneco Aysher 14
        ctx.fillStyle = "#ffd700"; ctx.fillRect(player.x-7*s, player.y-25*s, 14*s, 20*s);
        ctx.fillStyle = "#d2b48c"; ctx.beginPath(); ctx.arc(player.x, player.y-32*s, 6*s, 0, Math.PI*2); ctx.fill();

        // Joystick
        ctx.beginPath(); ctx.arc(joy.x, joy.y, joy.baseRadius, 0, Math.PI*2);
        ctx.fillStyle = 'rgba(255,255,255,0.1)'; ctx.fill();
        ctx.beginPath(); ctx.arc(joy.currX, joy.currY, joy.stickRadius, 0, Math.PI*2);
        ctx.fillStyle = '#00ff00'; ctx.fill();
    }

    canvas.addEventListener('pointerdown', e => {
        const rect = canvas.getBoundingClientRect();
        let tx = e.clientX - rect.left, ty = e.clientY - rect.top;
        if (Math.hypot(tx-joy.x, ty-joy.y) < joy.baseRadius*1.5) joy.active = true;
    });
    canvas.addEventListener('pointermove', e => {
        if (!joy.active) return;
        const rect = canvas.getBoundingClientRect();
        let dx = (e.clientX - rect.left) - joy.x, dy = (e.clientY - rect.top) - joy.y;
        let dist = Math.hypot(dx, dy), moveDist = Math.min(dist, joy.baseRadius), ang = Math.atan2(dy, dx);
        joy.currX = joy.x + Math.cos(ang) * moveDist;
        joy.currY = joy.y + Math.sin(ang) * moveDist;
    });
    canvas.addEventListener('pointerup', () => { joy.active = false; joy.currX = joy.x; joy.currY = joy.y; });

    update();
</script>
"""

components.html(game_code, height=530)

# Painel Lateral
st.sidebar.markdown("### 🏟️ CT GOAT TV")
st.sidebar.write("**Atleta:** Aysher Castro")
st.sidebar.write("**Status:** Condução Cirúrgica")
st.sidebar.markdown("---")
st.sidebar.info("Cuidado: Tanto o jogador quanto a bola derrubam os cones. Mantenha a bola no centro da linha verde.")
