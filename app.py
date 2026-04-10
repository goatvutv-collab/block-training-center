import streamlit as st
import streamlit.components.v1 as components

# Configuração focada em Mobile
st.set_page_config(page_title="KRYPTO CT", layout="centered")

# Estética da Federação (Título neon)
st.markdown("<h2 style='text-align: center; color: #00ffff; font-family: sans-serif;'>⚽ KRYPTO CT: TREINO DE PASSE</h2>", unsafe_allow_html=True)

# O Motor do Jogo (Injetando HTML5/JS com LERP)
game_code = """
<div style="display: flex; justify-content: center;">
    <canvas id="gameCanvas" width="360" height="500" style="background: #1e3d2b; border: 4px solid #00ffff; border-radius: 15px; touch-action: none;"></canvas>
</div>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');

    // Estado inicial: Bola na base, Alvo no topo
    let ball = { x: 180, y: 430, targetX: 180, targetY: 430, isMoving: false };
    let target = { x: 180, y: 100, radius: 25 };

    // Função LERP: Interpolação Linear para suavidade de PES
    function lerp(start, end, amt) {
        return (1 - amt) * start + amt * end;
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Desenha linhas do campo
        ctx.strokeStyle = "rgba(255,255,255,0.1)";
        ctx.strokeRect(20, 20, 320, 460);

        // Desenha o Alvo (Onde a nota 9.0 é gerada)
        ctx.beginPath();
        ctx.arc(target.x, target.y, target.radius, 0, Math.PI * 2);
        ctx.strokeStyle = "#00ffff";
        ctx.lineWidth = 3;
        ctx.stroke();

        // Lógica de Movimento com LERP
        if (ball.isMoving) {
            ball.x = lerp(ball.x, ball.targetX, 0.12);
            ball.y = lerp(ball.y, ball.targetY, 0.12);
            
            // Checa colisão com o alvo
            let dist = Math.hypot(ball.x - target.x, ball.y - target.y);
            if (dist < 10) {
                ball.isMoving = false;
                // Reset após o acerto
                setTimeout(() => { 
                    ball.x = 180; ball.y = 430; 
                    target.x = 50 + Math.random() * 260; // Muda alvo de lugar
                }, 500);
            }
        }

        // Desenha a Bola
        ctx.beginPath();
        ctx.arc(ball.x, ball.y, 10, 0, Math.PI * 2);
        ctx.fillStyle = "white";
        ctx.fill();
        
        requestAnimationFrame(draw);
    }

    // Controle por toque (Mobile)
    canvas.addEventListener('pointerdown', (e) => {
        const rect = canvas.getBoundingClientRect();
        ball.targetX = e.clientX - rect.left;
        ball.targetY = e.clientY - rect.top;
        ball.isMoving = true;
    });

    draw();
</script>
"""

# Renderiza o motor visual
components.html(game_code, height=550)

# Barra Lateral (Disfarce técnico)
st.sidebar.markdown("### 📊 Perfil do Atleta")
st.sidebar.write("Jogador: Aysher Castro")
st.sidebar.progress(85, text="Sincronização Tática")
st.sidebar.info("Calibrando motor físico LERP... (Oculto: Processando dados da rede)")
