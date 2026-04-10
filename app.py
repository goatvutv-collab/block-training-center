import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURAÇÃO DE ALTA PERFORMANCE
st.set_page_config(page_title="GOAT TV - CT MOBILE", layout="centered", initial_sidebar_state="collapsed")

# Estética Profissional da Federação
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h2 { text-shadow: 0 0 10px #00ff00; font-family: 'Trebuchet MS', sans-serif; margin-bottom: 5px; }
    .stProgress > div > div > div > div { background-color: #00ff00; }
    </style>
    <h2 style='text-align: center; color: #00ff00;'>GOAT TV: CENTRO DE TREINAMENTO</h2>
    <p style='text-align: center; color: #888; font-size: 12px;'>MÓDULO A: DRIBLE TÁTICO (PERSPECTIVA 2.5D)</p>
""", unsafe_allow_html=True)

# 2. MOTOR DO JOGO (VERSÃO LEVE)
game_code = """
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
    <canvas id="pesCanvas" width="380" height="550" style="background: #2d5a27; border: 3px solid #444; border-radius: 8px; touch-action: none;"></canvas>
    <div id="ui-info" style="color: #00ff00; font-family: monospace; font-size: 12px; margin-top: 10px;">SISTEMA LERP ATIVO | 60 FPS</div>
</div>

<script>
    const canvas = document.getElementById('pesCanvas');
    const ctx = canvas.getContext('2d');

    // Configuração do Atleta
    let player = { 
        x: 190, y: 450, targetX: 190, targetY: 450, 
        scale: 1, shirt: '#ffd700' 
    };
    
    // Cones do Circuito em U
    const cones = [
        {x: 80, y: 180}, {x: 300, y: 180},
        {x: 80, y: 380}, {x: 300, y: 380},
        {x: 190, y: 280}
    ];

    function lerp(start, end, amt) {
        return (1 - amt) * start + amt * end;
    }

    function drawField() {
        // Gramado PES Style
        for(let i=0; i<canvas.width; i+=40) {
            ctx.fillStyle = (i/40 % 2 === 0) ? '#2d5a27' : '#32612c';
            ctx.fillRect(i, 0, 40, canvas.height);
        }
        // Linhas de campo
        ctx.strokeStyle = "rgba(255,255,255,0.1)";
        ctx.beginPath();
        for(let i=0; i<=canvas.width; i+=60) {
            ctx.moveTo(i, 0); ctx.lineTo(i * 1.1 - 20, canvas.height);
        }
        ctx.stroke();
    }

    function drawHumanoid(x, y, scale) {
        ctx.save();
        ctx.translate(x, y);
        ctx.scale(scale, scale);
        // Sombra
        ctx.fillStyle = "rgba(0,0,0,0.2)";
        ctx.beginPath(); ctx.ellipse(0, 0, 15, 6, 0, 0, Math.PI*2); ctx.fill();
        // Pernas e Tronco
        ctx.fillStyle = "#222"; ctx.fillRect(-5, -12, 3, 12); ctx.fillRect(2, -12, 3, 12);
        ctx.fillStyle = player.shirt; ctx.fillRect(-8, -32, 16, 20);
        // Cabeça
        ctx.fillStyle = "#d2b48c"; ctx.beginPath(); ctx.arc(0, -38, 6, 0, Math.PI*2); ctx.fill();
        // Número 14
        ctx.fillStyle = "black"; ctx.font = "bold 9px Arial"; ctx.fillText("14", -5, -22);
        ctx.restore();
    }

    function drawCone(x, y) {
        let s = y / 450;
        ctx.fillStyle = "#ff6600";
        ctx.beginPath();
        ctx.moveTo(x - 10*s, y); ctx.lineTo(x + 10*s, y);
        ctx.lineTo(x, y - 25*s); ctx.fill();
        ctx.fillStyle = "#333"; ctx.fillRect(x - 11*s, y - 2, 22*s, 3);
    }

    function draw() {
        drawField();
        cones.forEach(c => drawCone(c.x, c.y));

        // Movimento LERP (Sem mineração, apenas física leve)
        if (Math.hypot(player.x - player.targetX, player.y - player.targetY) > 1) {
            player.x = lerp(player.x, player.targetX, 0.08);
            player.y = lerp(player.y, player.targetY, 0.08);
            player.scale = player.y / 450;
        }

        drawHumanoid(player.x, player.y, player.scale);
        requestAnimationFrame(draw);
    }

    canvas.addEventListener('pointerdown', (e) => {
        const rect = canvas.getBoundingClientRect();
        player.targetX = e.clientX - rect.left;
        player.targetY = e.clientY - rect.top;
    });

    draw();
</script>
"""

components.html(game_code, height=620)

# 3. SIDEBAR FOCADA EM JOGABILIDADE
st.sidebar.header("🏆 CARREIRA GOAT")
st.sidebar.subheader("Aysher Castro")
st.sidebar.write("Nível de Drible: **88**")
st.sidebar.write("Status: **Treino Aberto**")
st.sidebar.markdown("---")
st.sidebar.info("Foque em contornar os cones com precisão para aumentar sua nota de observação europeia.")

if st.sidebar.button("Finalizar Treino"):
    st.sidebar.balloons()
    st.sidebar.success("Dados de performance enviados!")
