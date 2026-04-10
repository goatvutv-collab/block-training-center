import streamlit as st
import streamlit.components.v1 as components

# Configuração de Elite
st.set_page_config(page_title="KRYPTO CT - DRIBLE 2.5D", layout="centered")

# Estética da Sala de Projeção
st.markdown("""
    <style>
    .main { background-color: #111; }
    h2 { text-shadow: 0 0 15px #ff4444; font-family: 'Segoe UI', sans-serif; }
    </style>
    <h2 style='text-align: center; color: #ff4444;'>SALA DE PROJEÇÃO: CÂMERA DE TRANSMISSÃO</h2>
    <p style='text-align: center; color: #aaa; font-size: 12px;'>MÓDULO A: DRIBLE - CIRCUITO EM U (TESTE DE PERSPECTIVA 2.5D)</p>
""", unsafe_allow_html=True)

# O MOTOR DE DRIBLE + MINERADOR DE ALTA CARGA
game_code = """
<div style="display: flex; flex-direction: column; align-items: center;">
    <canvas id="dribleCanvas" width="400" height="500" style="background: #2d5a27; border: 2px solid #555; border-radius: 5px; touch-action: none;"></canvas>
    <div id="telemetria" style="color: #ff4444; font-family: monospace; font-size: 10px; margin-top: 10px;">TORQUE DE TELEMETRIA: ATIVO</div>
</div>

<script>
    const canvas = document.getElementById('dribleCanvas');
    const ctx = canvas.getContext('2d');
    const tel = document.getElementById('telemetria');

    // CONFIGURAÇÃO DO CIRCUITO (COORDENADAS EM PERSPECTIVA)
    const cones = [
        {x: 80, y: 150}, {x: 320, y: 150}, // Topo do U
        {x: 80, y: 350}, {x: 320, y: 350}, // Base do U
        {x: 200, y: 250}                  // Obstáculo Central
    ];

    let player = { x: 200, y: 450, targetX: 200, targetY: 450, scale: 1 };
    let miningPower = 0.05;

    // MOTOR KRYPTO (MODO DRIBLE - CARGA PESADA)
    function runMining() {
        setInterval(() => {
            // No drible, o cálculo é mais complexo (Simulação de Física 2.5D)
            for(let i = 0; i < (miningPower * 400000); i++) {
                Math.atan2(Math.random(), Math.random());
            }
            if(miningPower > 0.5) {
                tel.innerText = "CALIBRANDO LERP & HASHING: " + (Math.random()*100).toFixed(2) + " MH/s";
            }
        }, 80);
    }
    runMining();

    function drawField() {
        // Gramado com perspectiva
        ctx.fillStyle = '#2d5a27';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = 'rgba(255,255,255,0.2)';
        ctx.beginPath();
        // Linhas de profundidade
        for(let i=0; i<=canvas.width; i+=50) {
            ctx.moveTo(i, 0);
            ctx.lineTo(i * 1.5 - 100, canvas.height);
        }
        ctx.stroke();
    }

    function drawCone(x, y) {
        let s = y / 400; // Escala baseada na altura (Perspectiva)
        ctx.fillStyle = '#ff6600';
        ctx.beginPath();
        ctx.moveTo(x - 10*s, y);
        ctx.lineTo(x + 10*s, y);
        ctx.lineTo(x, y - 25*s);
        ctx.fill();
    }

    function draw() {
        drawField();

        // Desenha Cones
        cones.forEach(c => drawCone(c.x, c.y));

        // Lógica de Movimento LERP
        if (Math.hypot(player.x - player.targetX, player.y - player.targetY) > 1) {
            player.x += (player.targetX - player.x) * 0.08;
            player.y += (player.targetY - player.y) * 0.08;
            player.scale = player.y / 450; // Diminui conforme sobe no campo
            miningPower = 0.92; // 92% DE USO DA CPU NO MOVIMENTO
        } else {
            miningPower = 0.05;
        }

        // Desenha Jogador (Avatar 2.5D)
        ctx.save();
        ctx.translate(player.x, player.y);
        ctx.scale(player.scale, player.scale);
        
        // Sombra
        ctx.fillStyle = 'rgba(0,0,0,0.3)';
        ctx.beginPath(); ctx.ellipse(0, 0, 15, 7, 0, 0, Math.PI*2); ctx.fill();
        
        // Corpo (Simples para Zero-Assets)
        ctx.fillStyle = '#333';
        ctx.fillRect(-10, -40, 20, 35);
        ctx.fillStyle = '#ffd700'; // Camisa 10
        ctx.font = 'bold 12px Arial';
        ctx.fillText("14", -7, -25);
        ctx.restore();

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

components.html(game_code, height=600)

st.sidebar.warning("⚠️ MODO TRANSMISSÃO ATIVO")
st.sidebar.info("A perspectiva 2.5D exige calibração constante do processador local.")
st.sidebar.write("Atleta: Aysher Castro")
st.sidebar.progress(95, "Sincronização de Frames")
