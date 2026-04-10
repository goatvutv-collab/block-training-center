import streamlit as st
import streamlit.components.v1 as components

# 1. CONFIGURAÇÃO DO CT MULTI-FASE
st.set_page_config(page_title="GOAT TV - EVOLUTION CT", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h3 { color: #00ff00; text-align: center; font-family: 'Courier New', monospace; margin-top: -30px; text-shadow: 0 0 10px #00ff00; }
    </style>
    <h3>🏟️ CT GOAT: DESAFIO DE PROGRESSÃO</h3>
""", unsafe_allow_html=True)

# 2. MOTOR DO JOGO COM SISTEMA DE FASES
game_code = """
<div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
    <div id="hud" style="color: white; font-family: monospace; margin-bottom: 5px; font-size: 12px; background: rgba(0,0,0,0.7); padding: 5px 15px; border-radius: 20px; border: 1px solid #333;">
        ESTÁGIO: <b id="phaseName" style="color: #ffd700;">1. CIRCUITO U</b> | 
        SCORE: <b id="scoreDisp" style="color: #00ff00;">1000</b>
    </div>
    <div style="position: relative;">
        <canvas id="gameCanvas" width="320" height="460" style="background: #1e3d1a; border: 2px solid #555; border-radius: 10px; touch-action: none;"></canvas>
        <div id="countdownOverlay" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #00ff00; font-size: 60px; font-family: sans-serif; font-weight: bold; text-shadow: 0 0 20px black; pointer-events: none;"></div>
    </div>
</div>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const phaseDisp = document.getElementById('phaseName');
    const scoreDisp = document.getElementById('scoreDisp');
    const countOverlay = document.getElementById('countdownOverlay');

    // CONFIGURAÇÕES
    let player = { x: 160, y: 410, speed: 3.6, radius: 10 };
    let ball = { x: 160, y: 385, radius: 6.5 };
    let score = 1000;
    let currentPhase = 1; // 1: U, 2: V, 3: Zig-Zag
    let currentGate = 0;
    let gameState = 'STARTING';
    let countNum = 3;
    let wobble = 0;

    // DEFINIÇÃO DOS CIRCUITOS
    const phases = {
        1: { name: "1. CIRCUITO U", gates: [
            {x1: 50, x2: 130, y: 320}, {x1: 50, x2: 130, y: 120}, 
            {x1: 190, x2: 270, y: 120}, {x1: 190, x2: 270, y: 320}
        ]},
        2: { name: "2. CIRCUITO V", gates: [
            {x1: 120, x2: 200, y: 350}, {x1: 40, x2: 100, y: 120}, 
            {x1: 220, x2: 280, y: 120}, {x1: 120, x2: 200, y: 350}
        ]},
        3: { name: "3. ZIG-ZAG", gates: [
            {x1: 40, x2: 100, y: 320}, {x1: 220, x2: 280, y: 240}, 
            {x1: 40, x2: 100, y: 160}, {x1: 220, x2: 280, y: 80}
        ]}
    };

    // Cones caídos
    let fallenCones = [];

    const joy = { x: 60, y: 380, baseRadius: 35, stickRadius: 18, currX: 60, currY: 380, active: false };

    function startCountdown() {
        gameState = 'STARTING';
        countNum = 3;
        let countInterval = setInterval(() => {
            if (countNum > 0) { countOverlay.innerText = countNum; countNum--; }
            else if (countNum === 0) { countOverlay.innerText = "GO!"; countNum--; }
            else { countOverlay.innerText = ""; gameState = 'PLAYING'; clearInterval(countInterval); }
        }, 1000);
    }
    startCountdown();

    function lerp(start, end, amt) { return (1 - amt) * start + amt * end; }

    function drawField() {
        ctx.fillStyle = '#1e3d1a'; ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = 'rgba(255,255,255,0.05)';
        for(let i=0; i<canvas.width; i+=40) ctx.strokeRect(i, 0, 1, canvas.height);
    }

    function drawCone(x, y, id) {
        let isDown = fallenCones.includes(id);
        let s = y / 460 + 0.5;
        if (isDown) {
            ctx.fillStyle = "rgba(150, 75, 0, 0.4)";
            ctx.beginPath(); ctx.ellipse(x, y, 12*s, 3*s, 0, 0, Math.PI*2); ctx.fill();
        } else {
            ctx.fillStyle = "#ff6600";
            ctx.beginPath(); ctx.moveTo(x-8*s, y); ctx.lineTo(x+8*s, y); ctx.lineTo(x, y-22*s); ctx.fill();
            ctx.fillStyle = "#222"; ctx.fillRect(x-9*s, y-1, 18*s, 3);
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
                
                wobble += 0.2;
                let targetBallX = player.x + vx * 6 + Math.cos(wobble) * 4;
                let targetBallY = player.y + vy * 6;
                ball.x = lerp(ball.x, targetBallX, 0.15);
                ball.y = lerp(ball.y, targetBallY, 0.15);
            }
        }

        // COLISÃO E SCORE
        let currentGates = phases[currentPhase].gates;
        currentGates.forEach((g, i) => {
            let id1 = `p${currentPhase}g${i}c1`;
            let id2 = `p${currentPhase}g${i}c2`;
            if (!fallenCones.includes(id1) && (Math.hypot(player.x-g.x1, player.y-g.y) < 18 || Math.hypot(ball.x-g.x1, ball.y-g.y) < 14)) { fallenCones.push(id1); score -= 50; }
            if (!fallenCones.includes(id2) && (Math.hypot(player.x-g.x2, player.y-g.y) < 18 || Math.hypot(ball.x-g.x2, ball.y-g.y) < 14)) { fallenCones.push(id2); score -= 50; }
        });
        scoreDisp.innerText = score;

        // LÓGICA DE PROGRESSÃO
        let gate = currentGates[currentGate];
        if (Math.hypot(ball.x - (gate.x1+gate.x2)/2, ball.y - gate.y) < 30) {
            currentGate++;
            if (currentGate >= currentGates.length) {
                currentGate = 0;
                if (currentPhase < 3) {
                    currentPhase++;
                    phaseDisp.innerText = phases[currentPhase].name;
                    player.x = 160; player.y = 410;
                    ball.x = 160; ball.y = 385;
                    startCountdown();
                } else {
                    gameState = 'FINISHED';
                    alert("🎖️ SCOUT FINALIZADO!\\nScore de Equilíbrio: " + score + "\\nAysher Castro está pronto para o próximo nível.");
                    location.reload();
                }
            }
        }

        player.x = Math.max(10, Math.min(310, player.x));
        player.y = Math.max(10, Math.min(450, player.y));
        render();
        requestAnimationFrame(update);
    }

    function render() {
        drawField();
        let currentGates = phases[currentPhase].gates;
        currentGates.forEach((g, i) => {
            drawCone(g.x1, g.y, `p${currentPhase}g${i}c1`);
            drawCone(g.x2, g.y, `p${currentPhase}g${i}c2`);
            if (i === currentGate) {
                ctx.beginPath(); ctx.moveTo(g.x1, g.y); ctx.lineTo(g.x2, g.y);
                ctx.strokeStyle = "rgba(0, 255, 0, 0.4)"; ctx.lineWidth = 4;
                ctx.setLineDash([5, 5]); ctx.stroke(); ctx.setLineDash([]);
            }
        });

        let s = player.y / 460 + 0.5;
        ctx.fillStyle = "rgba(0,0,0,0.2)"; ctx.beginPath(); ctx.ellipse(player.x, player.y, 12*s, 5*s, 0, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = "white"; ctx.beginPath(); ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = "#ffd700"; ctx.fillRect(player.x-7*s, player.y-25*s, 14*s, 20*s);
        ctx.fillStyle = "#d2b48c"; ctx.beginPath(); ctx.arc(player.x, player.y-32*s, 6*s, 0, Math.PI*2); ctx.fill();

        ctx.beginPath(); ctx.arc(joy.x, joy.y, joy.baseRadius, 0, Math.PI*2); ctx.fillStyle = 'rgba(255,255,255,0.05)'; ctx.fill();
        ctx.beginPath(); ctx.arc(joy.currX, joy.currY, joy.stickRadius, 0, Math.PI*2); ctx.fillStyle = '#00ff00'; ctx.fill();
    }

    canvas.addEventListener('pointerdown', e => {
        const rect = canvas.getBoundingClientRect();
        if (Math.hypot((e.clientX-rect.left)-joy.x, (e.clientY-rect.top)-joy.y) < 50) joy.active = true;
    });
    canvas.addEventListener('pointermove', e => {
        if (!joy.active) return;
        const rect = canvas.getBoundingClientRect();
        let dx = (e.clientX-rect.left)-joy.x, dy = (e.clientY-rect.top)-joy.y;
        let d = Math.min(Math.hypot(dx,dy), joy.baseRadius), a = Math.atan2(dy,dx);
        joy.currX = joy.x + Math.cos(a)*d; joy.currY = joy.y + Math.sin(a)*d;
    });
    canvas.addEventListener('pointerup', () => { joy.active=false; joy.currX=joy.x; joy.currY=joy.y; });
    update();
</script>
"""

components.html(game_code, height=530)

# SIDEBAR GOAT TV
st.sidebar.markdown("### 🏟️ RELATÓRIO DE CAMPO")
st.sidebar.write("**Atleta:** Aysher Castro")
st.sidebar.write("**Clube:** ASA de Arapiraca")
st.sidebar.markdown("---")
st.sidebar.success("Fase 1: U-Circuit")
st.sidebar.warning("Fase 2: V-Turn (Bloqueado)")
st.sidebar.error("Fase 3: Zig-Zag (Bloqueado)")
st.sidebar.markdown("---")
st.sidebar.info("O drible zig-zag é o teste final de equilíbrio. Mantenha a bola no centro.")
