import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURAÇÃO COMPACTA
st.set_page_config(page_title="GOAT TV - POCKET CT", layout="centered", initial_sidebar_state="collapsed")

# Cabeçalho Compacto
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h3 { color: #00ff00; text-align: center; font-family: sans-serif; margin-top: -30px; }
    </style>
    <h3>🎮 GOAT CT: DRIBLE PRO</h3>
""", unsafe_allow_html=True)

# 2. MOTOR DO JOGO COM ANALÓGICO FIXO
game_code = """
<div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
    <canvas id="gameCanvas" width="320" height="450" style="background: #244d20; border: 2px solid #444; border-radius: 10px; touch-action: none;"></canvas>
</div>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');

    // Configurações do Atleta e Mundo
    let player = { x: 160, y: 380, vx: 0, vy: 0, speed: 3, scale: 1 };
    const cones = [
        {x: 80, y: 120}, {x: 240, y: 120},
        {x: 80, y: 280}, {x: 240, y: 280},
        {x: 160, y: 200}
    ];

    // Configuração do Analógico
    const joy = { x: 60, y: 380, baseRadius: 40, stickRadius: 20, currX: 60, currY: 380, active: false };

    function drawField() {
        // Gramado simples e limpo
        ctx.fillStyle = '#244d20';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        ctx.strokeRect(10, 10, 300, 430);
    }

    function drawJoystick() {
        // Base do analógico
        ctx.beginPath();
        ctx.arc(joy.x, joy.y, joy.baseRadius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.fill();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.stroke();

        // Manche (o que move)
        ctx.beginPath();
        ctx.arc(joy.currX, joy.currY, joy.stickRadius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(0, 255, 0, 0.5)';
        ctx.fill();
    }

    function drawPlayer(x, y, scale) {
        ctx.save();
        ctx.translate(x, y);
        ctx.scale(scale, scale);
        // Sombra
        ctx.fillStyle = 'rgba(0,0,0,0.2)';
        ctx.beginPath(); ctx.ellipse(0, 0, 12, 5, 0, 0, Math.PI*2); ctx.fill();
        // Boneco 2.5D simplificado
        ctx.fillStyle = '#ffd700'; ctx.fillRect(-6, -25, 12, 18); // Camisa
        ctx.fillStyle = '#d2b48c'; ctx.beginPath(); ctx.arc(0, -32, 5, 0, Math.PI*2); ctx.fill(); // Cabeça
        ctx.restore();
    }

    function update() {
        if (joy.active) {
            let dx = joy.currX - joy.x;
            let dy = joy.currY - joy.y;
            let dist = Math.sqrt(dx*dx + dy*dy);
            if (dist > 0) {
                player.x += (dx / dist) * player.speed;
                player.y += (dy / dist) * player.speed;
            }
        }

        // Limites do campo
        player.x = Math.max(20, Math.min(300, player.x));
        player.y = Math.max(20, Math.min(430, player.y));
        player.scale = player.y / 450 + 0.5; // Efeito de perspectiva

        drawField();
        
        // Desenha cones
        ctx.fillStyle = '#ff6600';
        cones.forEach(c => {
            let s = c.y / 450 + 0.5;
            ctx.beginPath();
            ctx.moveTo(c.x - 8*s, c.y); ctx.lineTo(c.x + 8*s, c.y);
            ctx.lineTo(c.x, c.y - 20*s); ctx.fill();
        });

        drawPlayer(player.x, player.y, player.scale);
        drawJoystick();

        requestAnimationFrame(update);
    }

    // Controles Touch/Mouse para o Analógico
    canvas.addEventListener('pointerdown', handleStart);
    canvas.addEventListener('pointermove', handleMove);
    canvas.addEventListener('pointerup', handleEnd);

    function handleStart(e) {
        const rect = canvas.getBoundingClientRect();
        let touchX = e.clientX - rect.left;
        let touchY = e.clientY - rect.top;
        let dist = Math.sqrt(Math.pow(touchX - joy.x, 2) + Math.pow(touchY - joy.y, 2));
        if (dist < joy.baseRadius * 1.5) joy.active = true;
    }

    function handleMove(e) {
        if (!joy.active) return;
        const rect = canvas.getBoundingClientRect();
        let touchX = e.clientX - rect.left;
        let touchY = e.clientY - rect.top;
        
        let dx = touchX - joy.x;
        let dy = touchY - joy.y;
        let dist = Math.sqrt(dx*dx + dy*dy);
        
        if (dist < joy.baseRadius) {
            joy.currX = touchX;
            joy.currY = touchY;
        } else {
            joy.currX = joy.x + (dx / dist) * joy.baseRadius;
            joy.currY = joy.y + (dy / dist) * joy.baseRadius;
        }
    }

    function handleEnd() {
        joy.active = false;
        joy.currX = joy.x;
        joy.currY = joy.y;
    }

    update();
</script>
"""

components.html(game_code, height=480)

# Status Lateral Compacto
st.sidebar.markdown("### 🏃 ATLETA: AYSHER 14")
st.sidebar.write("Modo: **Drible Livre**")
st.sidebar.progress(100, text="Sistema Otimizado")
st.sidebar.caption("Analógico fixo habilitado para maior precisão nos cones.")
