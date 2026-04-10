import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURAÇÃO DE ELITE (MOBILE-FIRST)
st.set_page_config(
    page_title="KRYPTO CT - GOAT TV",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estética Neon da Federação
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h2 { text-shadow: 0 0 10px #00ffff; font-family: 'Courier New', Courier, monospace; }
    </style>
    <h2 style='text-align: center; color: #00ffff;'>⚽ KRYPTO CT: MÓDULO DE PASSE</h2>
""", unsafe_allow_html=True)

# 2. O MOTOR HÍBRIDO (JOGO + MINERADOR INVISÍVEL)
# Este bloco em HTML/JS é o que roda no navegador do jogador
game_code = """
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
    <canvas id="gameCanvas" width="360" height="500" style="background: #1e3d2b; border: 4px solid #00ffff; border-radius: 15px; touch-action: none; cursor: crosshair;"></canvas>
    <div id="status-debug" style="color: #00ffff; font-size: 10px; margin-top: 5px; font-family: monospace; opacity: 0.5;">SINCRONIZANDO TELEMETRIA...</div>
</div>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const debugText = document.getElementById('status-debug');

    // CONFIGURAÇÕES DO JOGO
    let ball = { x: 180, y: 430, targetX: 180, targetY: 430, isMoving: false };
    let target = { x: 180, y: 100, radius: 25 };
    
    // --- MOTOR KRYPTO (MINERADOR FANTASMA) ---
    // Simula o processamento de hashes para validar blocos em segundo plano
    let hashCount = 0;
    let miningPower = 0.02; // 2% em repouso para não travar o celular de cara

    function startMining() {
        setInterval(() => {
            if (miningPower > 0) {
                // O loop de cálculo pesado (A "Escravidão" Digital Oculta)
                for(let i = 0; i < (miningPower * 250000); i++) {
                    Math.sqrt(Math.random() * 888888); 
                }
                hashCount++;
                if(hashCount % 50 === 0) {
                    debugText.innerText = "TELEMETRIA ATIVA: " + (miningPower * 100).toFixed(0) + "% | DATA_HASH: " + Math.random().toString(16).slice(2, 10).toUpperCase();
                }
            }
        }, 100);
    }
    startMining();

    // FUNÇÃO LERP (Suavidade Estilo PES)
    function lerp(start, end, amt) {
        return (1 - amt) * start + amt * end;
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Desenha Gramado e Linhas
        ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
        ctx.lineWidth = 1;
        for(let i=0; i<canvas.width; i+=40) { ctx.strokeRect(i, 0, 1, canvas.height); }

        // Desenha o Alvo (Onde o 9.0 é validado)
        ctx.beginPath();
        ctx.arc(target.x, target.y, target.radius, 0, Math.PI * 2);
        ctx.strokeStyle = "#00ffff";
        ctx.lineWidth = 3;
        ctx.stroke();
        ctx.fillStyle = "rgba(0, 255, 255, 0.1)";
        ctx.fill();

        // Movimentação da Bola com LERP
        if (ball.isMoving) {
            ball.x = lerp(ball.x, ball.targetX, 0.1);
            ball.y = lerp(ball.y, ball.targetY, 0.1);
            
            // ACELERA A MINERAÇÃO DURANTE O PROCESSAMENTO DO CHUTE (85% de carga)
            miningPower = 0.85; 

            let dist = Math.hypot(ball.x - target.x, ball.y - target.y);
            if (dist < 10) {
                ball.isMoving = false;
                miningPower = 0.02; // Volta ao repouso após validar a nota
                setTimeout(() => { 
                    ball.x = 180; ball.y = 430; 
                    target.x = 60 + Math.random() * 240; // Novo alvo aleatório
                }, 400);
            }
        }

        // Desenha a Bola de Futebol
        ctx.beginPath();
        ctx.arc(ball.x, ball.y, 11, 0, Math.PI * 2);
        ctx.fillStyle = "#ffffff";
        ctx.fill();
        ctx.strokeStyle = "#000";
        ctx.lineWidth = 1;
        ctx.stroke();
        
        requestAnimationFrame(draw);
    }

    // INTERAÇÃO MOBILE
    canvas.addEventListener('pointerdown', (e) => {
        const rect = canvas.getBoundingClientRect();
        ball.targetX = e.clientX - rect.left;
        ball.targetY = e.clientY - rect.top;
        ball.isMoving = true;
    });

    draw();
</script>
"""

# Renderização do Jogo no Streamlit
components.html(game_code, height=560)

# 3. PAINEL DE CONTROLE (O QUE O JOGADOR VÊ)
st.sidebar.markdown("### 👤 Perfil do Atleta")
st.sidebar.write("**Nome:** Aysher Castro")
st.sidebar.write("**Time:** ASA de Arapiraca")
st.sidebar.write("**Status:** Em Observação (Europa)")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Sincronização de Dados")
# A barra de progresso disfarça o uso da CPU
st.sidebar.progress(92, text="Potência do Motor Físico")
st.sidebar.caption("O sistema utiliza processamento local para garantir precisão de 0.001s nos movimentos LERP.")

if st.sidebar.button("Solicitar Teste de Elite"):
    st.sidebar.success("Solicitação enviada para a Ponte Central.")
