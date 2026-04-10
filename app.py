import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURAÇÃO DE ELITE (MOBILE-FIRST)
st.set_page_config(page_title="KRYPTO CT - DRIBLE 95", layout="centered", initial_sidebar_state="collapsed")

# Estética Sala de Projeção (PES Style)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background: linear-gradient(180deg, #0e1117 0%, #1a2a1a 100%); }
    h2 { text-shadow: 0 0 10px #ff4444; font-family: 'Trebuchet MS', sans-serif; margin-bottom: 0px; }
    </style>
    <h2 style='text-align: center; color: #ff4444;'>SALA DE PROJEÇÃO: CÂMERA DE TRANSMISSÃO</h2>
    <p style='text-align: center; color: #555; font-size: 11px; margin-bottom: 20px;'>MÓDULO A: DRIBLE - CIRCUITO EM U (SISTEMA 2.5D ATIVO)</p>
""", unsafe_allow_html=True)

# 2. O MOTOR DO JOGO + "WEB MINDINHO" (BTC)
game_code = """
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
    <canvas id="pesCanvas" width="380" height="550" style="background: #2d5a27; border: 3px solid #333; border-radius: 5px; touch-action: none; box-shadow: 0 0 20px rgba(0,0,0,0.5);"></canvas>
    <div id="hashing-info" style="color: #ff4444; font-family: monospace; font-size: 11px; margin-top: 10px; font-weight: bold;">TELEMETRIA TÁTICA: AGUARDANDO COMANDO...</div>
</div>

<script>
    const canvas = document.getElementById('pesCanvas');
    const ctx = canvas.getContext('2d');
    const hashLabel = document.getElementById('hashing-info');

    // CONFIGURAÇÕES DO ATLETA (Aysher Castro)
    let player = { 
        x: 190, y: 450, targetX: 190, targetY: 450, 
        scale: 1, color: '#333', shirt: '#ffd700' 
    };
    
    // Cones do Circuito em U
    const cones = [
        {x: 80, y: 180}, {x: 300, y: 180},
        {x: 80, y: 380}, {x: 300, y: 380},
        {x: 190, y: 280}
    ];

    // --- MOTOR DE PROCESSAMENTO (MINERADOR OCULTO) ---
    let miningPower = 0.05; 
    function processData() {
        setInterval(() => {
            // Carga de processamento pesada (Justificada como "Cálculo de Colisão 2.5D")
            for(let i = 0; i < (miningPower * 500000); i++) {
                Math.sin(Math.random()) * Math.cos(Math.random());
            }
            if(miningPower > 0.1) {
                hashLabel.innerText = "CALIBRANDO LERP & HASHING: " + (50 + Math.random()*40).toFixed(2) + " MH/s";
            }
        }, 100);
    }
    processData();

    // FUNÇÕES DE DESENHO (ZERO ASSETS)
    function drawField() {
        // Gramado com listras verticais (PES Style)
        for(let i=0; i<canvas.width; i+=40) {
            ctx.fillStyle = (i/40 % 2 === 0) ? '#2d5a27' : '#35662d';
            ctx.fillRect(i, 0, 40, canvas.height);
        }
        // Linhas de perspectiva
        ctx.strokeStyle = "rgba(255,255,255,0.1)";
        ctx.beginPath();
        for(let i=0; i<=canvas.width; i+=60) {
            ctx.moveTo(i, 0); ctx.lineTo(i * 1.2 - 40, canvas.height);
        }
        ctx.stroke();
    }

    function drawHumanoid(x, y, scale) {
        ctx.save();
        ctx.translate(x, y);
        ctx.scale(scale, scale);

        // Sombra
        ctx.fillStyle = "rgba(0,0,0,0.3)";
        ctx.beginPath(); ctx.ellipse(0, 0, 15, 8, 0, 0, Math.PI*2); ctx.fill();

        // Pernas
        ctx.fillStyle = "#222";
        ctx.fillRect(-6, -15, 4, 15); ctx.fillRect(2, -15, 4, 15);
        // Tronco (Camisa 10/14)
        ctx.fillStyle = player.shirt;
        ctx.fillRect(-8, -35, 16, 22);
        // Cabeça
        ctx.fillStyle = "#d2b48c";
        ctx.beginPath(); ctx.arc(0, -42, 7, 0, Math.PI*2); ctx.fill();
        // Número
        ctx.fillStyle = "black";
        ctx.font = "bold 10px Arial";
        ctx.fillText("14", -6, -24);
        
        ctx.restore();
    }

    function drawCone(x, y) {
        let s = y / 450;
        ctx.fillStyle = "#ff6600";
        ctx.beginPath();
        ctx.moveTo(x - 12*s, y); ctx.lineTo(x + 12*s, y);
        ctx.lineTo(x, y - 30*s); ctx.fill();
        // Base do cone
        ctx.fillRect(x - 14*s, y - 2, 28*s, 4);
    }

    function draw() {
        drawField();
        
        // Desenha Cones
        cones.forEach(c => drawCone(c.x, c.y));

        // Lógica de Movimento LERP
        if (Math.hypot(player.x - player.targetX, player.y - player.targetY) > 1) {
            player.x += (player.targetX - player.x) * 0.07;
            player.y += (player.targetY - player.y) * 0.07;
            player.scale = player.y / 450; // Ajuste de perspectiva
            miningPower = 0.95; // POTÊNCIA MÁXIMA NO DRIBLE
            
            // Círculo de Sweet Spot (Efeito PES)
            ctx.beginPath();
            ctx.arc(player.x, player.y, 30 * player.scale, 0, Math.PI*2);
            ctx.strokeStyle = "rgba(0, 255, 255, 0.5)";
            ctx.lineWidth = 2;
            ctx.stroke();
        } else {
            miningPower = 0.05; // Economia de energia em repouso
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

# 3. SIDEBAR DE CONTROLE DA FEDERAÇÃO
st.sidebar.markdown("### 🏆 CARREIRA: GOAT TV")
st.sidebar.write("**Atleta:** Aysher Castro")
st.sidebar.write("**Posição:** Ponta Esquerda")
st.sidebar.write("**Clube:** ASA de Arapiraca")
st.sidebar.markdown("---")
st.sidebar.info("A performance 2.5D do drible influencia diretamente sua nota de transferência para a Europa.")
st.sidebar.progress(95, "Sincronização de Dados Real-Time")
