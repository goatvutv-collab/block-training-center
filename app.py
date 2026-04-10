import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURAÇÃO DO DESAFIO
st.set_page_config(page_title="GOAT TV - CIRCUITO PRO", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h3 { color: #00ff00; text-align: center; font-family: sans-serif; margin-top: -30px; text-shadow: 0 0 10px #00ff00; }
    </style>
    <h3>⏱️ DESAFIO: 5 VOLTAS CRONOMETRADAS</h3>
""", unsafe_allow_html=True)

# 2. MOTOR DO JOGO COM CIRCUITO E TEMPO
game_code = """
<div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
    <div id="hud" style="color: white; font-family: monospace; margin-bottom: 5px; font-size: 14px; background: rgba(0,0,0,0.5); padding: 5px 15px; border-radius: 20px;">
        VOLTAS: <span id="lapCount" style="color: #00ff00;">0/5</span> | 
        TEMPO: <span id="timer" style="color: #ff4444;">60.0s</span>
    </div>
    <canvas id="gameCanvas" width="320" height="450" style="background: #244d20; border: 2px solid #555; border-radius: 10px; touch-action: none;"></canvas>
</div>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const lapDisp = document.getElementById('lapCount');
    const timeDisp = document.getElementById('timer');

    // Estado do Jogo
    let player = { x: 160, y: 380, speed: 3.5, scale: 1 };
    let laps = 0;
    let timeLeft = 60.0;
    let gameActive = true;
    let currentCheckpoint = 0;

    // Definição do Circuito (Portões que o jogador deve passar)
    const checkpoints = [
        {x: 60, y: 320, label: '1'},  // Início (Esquerda Baixo)
        {x: 60, y: 120, label: '2'},  // Topo Esquerda
        {x: 260, y: 120, label: '3'}, // Topo Direita
        {x: 260, y: 320, label: '4'}  // Fim da volta (Direita Baixo)
    ];

    const joy = { x: 60, y: 380, baseRadius: 35, stickRadius: 18, currX: 60, currY: 380, active: false };

    function drawField() {
        ctx.fillStyle = '#244d20';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Linhas do Circuito (Guia visual)
        ctx.setLineDash([5, 5]);
        ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        ctx.beginPath();
        ctx.moveTo(checkpoints[0].x, checkpoints[0].y);
        checkpoints.forEach(p => ctx.lineTo(p.x, p.y));
        ctx.stroke();
        ctx.setLineDash([]);
    }

    function drawCheckpoints() {
        checkpoints.forEach((cp, index) => {
            let isNext = (index === currentCheckpoint);
            ctx.beginPath();
            ctx.arc(cp.x, cp.y, 15, 0, Math.PI * 2);
            ctx.fillStyle = isNext ? 'rgba(0, 255, 0, 0.4)' : 'rgba(255, 255, 255, 0.1)';
            ctx.fill();
            ctx.strokeStyle = isNext ? '#00ff00' : '#555';
            ctx.stroke();
        });
    }

    function update() {
        if (!gameActive) return;

        // Movimento do Jogador
        if (joy.active) {
            let dx = joy.currX - joy.x;
            let dy = joy.currY - joy.y;
            let dist = Math.sqrt(dx*dx + dy*dy);
            if (dist > 0) {
                player.x += (dx / dist) * player.speed;
                player.y += (dy / dist) * player.speed;
            }
        }

        // Lógica de Checkpoint (Colisão)
        let target = checkpoints[currentCheckpoint];
        let distToCP = Math.sqrt(Math.pow(player.x - target.x, 2) + Math.pow(player.y - target.y, 2));
        
        if (distToCP < 25) {
            currentCheckpoint++;
            if (currentCheckpoint >= checkpoints.length) {
                currentCheckpoint = 0;
                laps++;
                lapDisp.innerText = laps + "/5";
                if (laps >= 5) winGame();
            }
        }

        // Cronômetro
        timeLeft -= 1/60;
        timeDisp.innerText = Math.max(0, timeLeft).toFixed(1) + "s";
        if (timeLeft <= 0) loseGame();

        render();
        requestAnimationFrame(update);
    }

    function render() {
        drawField();
        drawCheckpoints();
        
        // Sombra e Boneco
        ctx.fillStyle = 'rgba(0,0,0,0.2)';
        ctx.beginPath(); ctx.ellipse(player.x, player.y, 12, 5, 0, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = '#ffd700'; ctx.fillRect(player.x-6, player.y-25, 12, 18);
        ctx.fillStyle = '#d2b48c'; ctx.beginPath(); ctx.arc(player.x, player.y-32, 5, 0, Math.PI*2); ctx.fill();

        // Analógico
        ctx.beginPath(); ctx.arc(joy.x, joy.y, joy.baseRadius, 0, Math.PI*2);
        ctx.fillStyle = 'rgba(255,255,255,0.1)'; ctx.fill();
        ctx.beginPath(); ctx.arc(joy.currX, joy.currY, joy.stickRadius, 0, Math.PI*2);
        ctx.fillStyle = '#00ff00'; ctx.fill();
    }

    function winGame() {
        gameActive = false;
        alert("TREINO CONCLUÍDO! Status: Elite (Nota 9.0)");
        location.reload();
    }

    function loseGame() {
        gameActive = false;
        alert("TEMPO ESGOTADO! Tente novamente para atingir a meta.");
        location.reload();
    }

    // Handlers do Analógico
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

components.html(game_code, height=520)

# Sidebar
st.sidebar.markdown("### 🏟️ TESTE DE APTIDÃO")
st.sidebar.write("Objetivo: **5 Voltas**")
st.sidebar.write("Tempo: **60 segundos**")
st.sidebar.markdown("---")
st.sidebar.info("Passe pelos portões verdes em ordem para completar as voltas. A precisão define sua nota final.")
