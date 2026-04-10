import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURAÇÃO DO DESAFIO DE ELITE
st.set_page_config(page_title="GOAT TV - CIRCUITO PRO", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h3 { color: #00ff00; text-align: center; font-family: sans-serif; margin-top: -30px; text-shadow: 0 0 10px #00ff00; }
    </style>
    <h3>🏆 DESAFIO: CIRCUITO DE CONES</h3>
""", unsafe_allow_html=True)

# 2. MOTOR DO JOGO COM CONES, LINHA VERDE E COUNTDOWN
game_code = """
<div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
    <div id="hud" style="color: white; font-family: monospace; margin-bottom: 5px; font-size: 14px; background: rgba(0,0,0,0.5); padding: 5px 15px; border-radius: 20px;">
        VOLTAS: <span id="lapCount" style="color: #00ff00;">0/5</span> | 
        TEMPO: <span id="timer" style="color: #ff4444;">60.0s</span>
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
    const countOverlay = document.getElementById('countdownOverlay');

    // Estado do Jogo
    let player = { x: 160, y: 400, speed: 3.2, scale: 1 };
    let laps = 0;
    let timeLeft = 60.0;
    let currentGate = 0;
    let gameState = 'STARTING'; // STARTING, PLAYING, FINISHED
    let countNum = 3;

    // Definição dos Portões (Pares de cones + Linha)
    const gates = [
        { x1: 40, x2: 120, y: 320, label: '1' }, // Esquerda Baixo
        { x1: 40, x2: 120, y: 120, label: '2' }, // Topo Esquerda
        { x1: 200, x2: 280, y: 120, label: '3' }, // Topo Direita
        { x1: 200, x2: 280, y: 320, label: '4' }  // Direita Baixo
    ];

    const joy = { x: 60, y: 380, baseRadius: 35, stickRadius: 18, currX: 60, currY: 380, active: false };

    // Iniciar Contagem Regressiva
    let countInterval = setInterval(() => {
        if (countNum > 0) {
            countOverlay.innerText = countNum;
            countNum--;
        } else if (countNum === 0) {
            countOverlay.innerText = "GO!";
            countNum--;
        } else {
            countOverlay.innerText = "";
            gameState = 'PLAYING';
            clearInterval(countInterval);
        }
    }, 1000);

    function drawCone(x, y, s) {
        ctx.fillStyle = "#ff6600";
        ctx.beginPath();
        ctx.moveTo(x - 8*s, y); ctx.lineTo(x + 8*s, y);
        ctx.lineTo(x, y - 20*s); ctx.fill();
        ctx.fillStyle = "#333"; ctx.fillRect(x - 9*s, y - 2, 18*s, 3);
    }

    function drawField() {
        ctx.fillStyle = '#244d20';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = 'rgba(255,255,255,0.05)';
        for(let i=0; i<canvas.width; i+=40) ctx.strokeRect(i,0,1,canvas.height);
    }

    function update() {
        if (gameState !== 'PLAYING') {
            render();
            requestAnimationFrame(update);
            return;
        }

        // Movimento
        if (joy.active) {
            let dx = joy.currX - joy.x;
            let dy = joy.currY - joy.y;
            let dist = Math.hypot(dx, dy);
            if (dist > 0) {
                player.x += (dx / dist) * player.speed;
                player.y += (dy / dist) * player.speed;
            }
        }

        // Lógica de Portão (Cruzar a linha verde)
        let gate = gates[currentGate];
        let midX = (gate.x1 + gate.x2) / 2;
        let distToLine = Math.hypot(player.x - midX, player.y - gate.y);
        
        if (distToLine < 30) {
            currentGate++;
            if (currentGate >= gates.length) {
                currentGate = 0;
                laps++;
                lapDisp.innerText = laps + "/5";
                if (laps >= 5) { gameState = 'FINISHED'; alert("🏆 ELITE: 9.0! Carreira na Europa desbloqueada."); location.reload(); }
            }
        }

        timeLeft -= 1/60;
        timeDisp.innerText = Math.max(0, timeLeft).toFixed(1) + "s";
        if (timeLeft <= 0) { gameState = 'FINISHED'; alert("⏳ TEMPO ESGOTADO! Treine mais a agilidade."); location.reload(); }

        render();
        requestAnimationFrame(update);
    }

    function render() {
        drawField();

        // Desenhar Portões e Cones
        gates.forEach((g, i) => {
            let s = g.y / 450 + 0.5;
            drawCone(g.x1, g.y, s);
            drawCone(g.x2, g.y, s);
            
            // Linha Verde de Alvo
            if (i === currentGate) {
                ctx.beginPath();
                ctx.moveTo(g.x1, g.y);
                ctx.lineTo(g.x2, g.y);
                ctx.strokeStyle = "#00ff00";
                ctx.lineWidth = 4;
                ctx.setLineDash([5, 3]);
                ctx.stroke();
                ctx.setLineDash([]);
                // Brilho da linha
                ctx.shadowBlur = 10; ctx.shadowColor = "#00ff00"; ctx.stroke(); ctx.shadowBlur = 0;
            }
        });
        
        // Atleta (Aysher 14)
        player.scale = player.y / 450 + 0.5;
        ctx.fillStyle = 'rgba(0,0,0,0.2)';
        ctx.beginPath(); ctx.ellipse(player.x, player.y, 12*player.scale, 5*player.scale, 0, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = '#ffd700'; ctx.fillRect(player.x-6*player.scale, player.y-25*player.scale, 12*player.scale, 18*player.scale);
        ctx.fillStyle = '#d2b48c'; ctx.beginPath(); ctx.arc(player.x, player.y-32*player.scale, 5*player.scale, 0, Math.PI*2); ctx.fill();

        // Analógico
        ctx.beginPath(); ctx.arc(joy.x, joy.y, joy.baseRadius, 0, Math.PI*2);
        ctx.fillStyle = 'rgba(255,255,255,0.1)'; ctx.fill();
        ctx.beginPath(); ctx.arc(joy.currX, joy.currY, joy.stickRadius, 0, Math.PI*2);
        ctx.fillStyle = '#00ff00'; ctx.fill();
    }

    // Eventos do Joystick
    canvas.addEventListener('pointerdown', e => {
        const rect = canvas.getBoundingClientRect();
        let tx = e.clientX - rect.left; let ty = e.clientY - rect.top;
        if (Math.hypot(tx-joy.x, ty-joy.y) < joy.baseRadius*1.5) joy.active = true;
    });
    canvas.addEventListener('pointermove', e => {
        if (!joy.active) return;
        const rect = canvas.getBoundingClientRect();
        let tx = e.clientX - rect.left; let ty = e.clientY - rect.top;
        let dx = tx - joy.x; let dy = ty - joy.y;
        let dist = Math.hypot(dx, dy);
        let ang = Math.atan2(dy, dx);
        let moveDist = Math.min(dist, joy.baseRadius);
        joy.currX = joy.x + Math.cos(ang) * moveDist;
        joy.currY = joy.y + Math.sin(ang) * moveDist;
    });
    canvas.addEventListener('pointerup', () => {
        joy.active = false; joy.currX = joy.x; joy.currY = joy.y;
    });

    update();
</script>
"""

components.html(game_code, height=530)

# Painel da Federação
st.sidebar.markdown("### 🏟️ CIRCUITO DE ELITE")
st.sidebar.write("Atleta: **Aysher Castro**")
st.sidebar.write("Meta: **5 Voltas em 60s**")
st.sidebar.markdown("---")
st.sidebar.success("Cruze a linha VERDE piscante para validar o portão.")
st.sidebar.info("A contagem de 3 segundos permite o ajuste do grip no celular.")
