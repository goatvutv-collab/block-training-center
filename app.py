import streamlit as st
import streamlit.components.v1 as components
import json

# 1. CONFIGURAÇÃO GOAT TV
st.set_page_config(page_title="GOAT TV - CT ARCADE v16.1", layout="centered", initial_sidebar_state="collapsed")

# Atributos baseados no Dossiê
DNA_ATTRS = ["Condução", "Velocidade", "Drible"]
TRAVA_ATTRS = ["Desarme", "Impacto Físico"]

if 'app_mode' not in st.session_state:
    st.session_state.app_mode = 'LOBBY'

# --- TELA 1: LOBBY ---
if st.session_state.app_mode == 'LOBBY':
    st.markdown("<h2 style='text-align: center; color: #ffd700;'>🏟️ LOBBY GOAT TV</h2>", unsafe_allow_html=True)
    st.write("---")
    col1, col2 = st.columns([1, 1.2])
    with col1:
        tipo_treino = st.selectbox("SETOR:", ["DRIBLE", "PASSE", "CHUTE"])
        if st.button("INICIAR TREINO 🏟️", use_container_width=True):
            st.session_state.tipo_selecionado = tipo_treino
            st.session_state.app_mode = 'TRAINING'
            st.rerun()
    with col2:
        st.markdown("### 📊 Evolução de Arquétipo")
        st.success("📈 DNA: " + ", ".join(DNA_ATTRS))
        st.error("📉 TRAVA: " + ", ".join(TRAVA_ATTRS))
        st.info("💡 Feedback tátil, sonoro e relatório completo de habilidades ativado.")

# --- TELA 2: CAMPO DE TREINAMENTO ---
elif st.session_state.app_mode == 'TRAINING':
    tipo = st.session_state.tipo_selecionado
    
    fases_json = {
        "DRIBLE": """{
            1: {startPos:{x:160, y:410}, gates:[{x1:60,x2:120,y:320},{x1:60,x2:120,y:150},{x1:200,x2:260,y:150},{x1:200,x2:260,y:320}], enemies:[]},
            2: {startPos:{x:160, y:410}, gates:[{x1:40,x2:100,y:350},{x1:220,x2:280,y:250},{x1:40,x2:100,y:150},{x1:130,x2:190,y:80}], enemies:[]},
            3: {startPos:{x:160, y:410}, 
                gates:[{x1:220,x2:280,y:380},{x1:40,x2:100,y:300},{x1:220,x2:280,y:220},{x1:40,x2:100,y:140},{x1:130,x2:190,y:60}], 
                enemies:[
                    {x:100, y:340, centerX:100, centerY:340, rangeX:120, rangeY:0, speedX:1.5, speedY:0, dirX:1, dirY:0, type:'H'},
                    {x:220, y:340, centerX:220, centerY:340, rangeX:120, rangeY:0, speedX:1.5, speedY:0, dirX:-1, dirY:0, type:'H'},
                    {x:160, y:180, centerX:160, centerY:180, rangeX:90, rangeY:40, speedX:1.3, speedY:0.8, dirX:1, dirY:1, type:'D'},
                    {x:160, y:100, centerX:160, centerY:100, rangeX:90, rangeY:30, speedX:1.3, speedY:0.6, dirX:-1, dirY:-1, type:'D'}
                ]}
        }""",
        "PASSE": "{1: {startPos:{x:160, y:410}, gates:[{x1:130,x2:190,y:100}]}, 2: {startPos:{x:160, y:410}, gates:[{x1:40,x2:100,y:150}]}, 3: {startPos:{x:160, y:410}, gates:[{x1:220,x2:280,y:150}]}}",
        "CHUTE": "{1: {startPos:{x:160, y:410}, gates:[{x1:100,x2:220,y:120}]}, 2: {startPos:{x:160, y:410}, gates:[{x1:80,x2:240,y:100}]}, 3: {startPos:{x:160, y:410}, gates:[{x1:140,x2:180,y:80}]}}"
    }

    game_code = f"""
    <div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
        <div id="hud" style="color: white; font-family: monospace; margin-bottom: 5px; font-size: 11px; background: #000; padding: 5px 15px; border-radius: 10px; border: 1px solid #ffd700; width: 310px; display: flex; justify-content: space-between;">
            <span>ETAPA: <b id="phaseDisp" style="color: #0f0;">1/3</b></span>
            <span>MODO: <b id="modeDisp" style="color: #ffd700;">IDA</b></span>
            <span>SCORE: <b id="scoreDisp" style="color: #0f0;">1000</b></span>
        </div>
        <canvas id="gameCanvas" width="320" height="600" style="background: #111; border: 4px solid #333; border-radius: 10px; touch-action: none;"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreDisp = document.getElementById('scoreDisp');
        const phaseDisp = document.getElementById('phaseDisp');
        const modeDisp = document.getElementById('modeDisp');

        // ÁUDIO E HÁPTICO
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playWhistle() {{
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(850, audioCtx.currentTime); 
            osc.frequency.exponentialRampToValueAtTime(1250, audioCtx.currentTime + 0.1);
            gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.start(); osc.stop(audioCtx.currentTime + 0.2);
        }}

        function triggerHaptic(ms) {{ if (navigator.vibrate) navigator.vibrate(ms); }}

        let player = {{ x: 160, y: 410, speed: 1.5, hitTimer: 0 }};
        let ball = {{ x: 160, y: 385 }};
        let score = 1000;
        let currentPhase = 1;
        let currentGate = 0;
        let direction = 1; 
        let gameState = 'COUNTDOWN';
        let countdown = 3;
        let fallenCones = [];

        const phases = {fases_json[tipo]};
        const joy = {{ x: 160, y: 530, baseRadius: 45, currX: 160, currY: 530, active: false }};

        function getScale(y) {{ return (y / 460) * 0.55 + 0.45; }}

        function drawCone(x, y, id) {{
            let s = getScale(y);
            let isDown = fallenCones.includes(id);
            if (isDown) {{
                ctx.fillStyle = "rgba(255,100,0,0.3)";
                ctx.beginPath(); ctx.ellipse(x, y, 14*s, 5*s, 0, 0, Math.PI*2); ctx.fill();
            }} else {{
                ctx.fillStyle = "#ff6600";
                ctx.beginPath(); ctx.moveTo(x-8*s, y); ctx.lineTo(x+8*s, y); ctx.lineTo(x, y-22*s); ctx.fill();
            }}
        }}

        function initModule(phase) {{
            gameState = 'COUNTDOWN'; countdown = 3;
            const config = phases[phase];
            player.x = config.startPos.x; player.y = config.startPos.y;
            ball.x = player.x; ball.y = player.y - 25;
            currentGate = 0; direction = 1; fallenCones = [];
            modeDisp.innerText = "IDA";
            let timer = setInterval(() => {{ countdown--; if(countdown <= 0) {{ clearInterval(timer); gameState = 'PLAYING'; }} }}, 1000);
        }}

        function update() {{
            if (gameState === 'FINISHED') return;
            if (player.hitTimer > 0) player.hitTimer--;

            if (gameState === 'PLAYING') {{
                if (joy.active) {{
                    let dx = joy.currX - joy.x, dy = joy.currY - joy.y, d = Math.hypot(dx, dy);
                    if (d > 3) {{ 
                        let vx = (dx/d)*player.speed, vy = (dy/d)*player.speed;
                        let margin = 20 * getScale(player.y);
                        // BORDAS RÍGIDAS
                        if(player.x+vx > margin && player.x+vx < 320-margin) player.x += vx;
                        if(player.y+vy > 10 && player.y+vy < 450) player.y += vy;
                        ball.x += (player.x - ball.x) * 0.25;
                        ball.y += (player.y - 22*getScale(player.y) - ball.y) * 0.25;
                    }}
                }}

                let phaseData = phases[currentPhase];
                if(phaseData.enemies) {{
                    phaseData.enemies.forEach(e => {{
                        e.x += e.speedX * e.dirX; e.y += e.speedY * e.dirY;
                        if (Math.abs(e.x - e.centerX) > e.rangeX/2) e.dirX *= -1;
                        if (e.type === 'D' && Math.abs(e.y - e.centerY) > e.rangeY/2) e.dirY *= -1;
                        if (Math.hypot(player.x - e.x, player.y - e.y) < 18*getScale(e.y)) {{
                            score -= 0.7; player.hitTimer = 10;
                            if(Math.floor(Date.now()/500) % 2 === 0) triggerHaptic(40);
                        }}
                    }});
                }}

                let phaseGates = phaseData.gates;
                phaseGates.forEach((g, i) => {{
                    let id1 = `p${{currentPhase}}g${{i}}a`, id2 = `p${{currentPhase}}g${{i}}b`;
                    let s = getScale(g.y);
                    if (!fallenCones.includes(id1) && Math.hypot(player.x-g.x1, player.y-g.y) < 12*s) {{ 
                        fallenCones.push(id1); score -= 50; playWhistle(); triggerHaptic(100); 
                    }}
                    if (!fallenCones.includes(id2) && Math.hypot(player.x-g.x2, player.y-g.y) < 12*s) {{ 
                        fallenCones.push(id2); score -= 50; playWhistle(); triggerHaptic(100); 
                    }}
                }});

                let gate = phaseGates[currentGate];
                if (Math.hypot(ball.x - (gate.x1+gate.x2)/2, ball.y - gate.y) < 25) {{
                    currentGate += direction;
                    if (currentGate >= phaseGates.length) {{ direction = -1; currentGate = phaseGates.length - 2; modeDisp.innerText = "VOLTA"; }}
                    else if (currentGate < 0) {{
                        if (currentPhase < 3) {{ currentPhase++; phaseDisp.innerText = currentPhase+"/3"; initModule(currentPhase); }}
                        else {{ gameState = 'FINISHED'; }}
                    }}
                }}
            }}
            scoreDisp.innerText = Math.floor(score);
            render();
            requestAnimationFrame(update);
        }}

        function render() {{
            ctx.fillStyle = '#1e3d1a'; ctx.fillRect(0,0,320,460);
            ctx.fillStyle = '#050505'; ctx.fillRect(0,460,320,140);
            ctx.strokeStyle = "rgba(255,255,255,0.08)";
            for(let i=-100; i<=420; i+=40) {{ ctx.beginPath(); ctx.moveTo(160, -80); ctx.lineTo(i*1.5-80, 460); ctx.stroke(); }}

            let phaseData = phases[currentPhase];
            let drawList = [];
            phaseData.gates.forEach((g, i) => drawList.push({{ type: 'gate', y: g.y, data: g, index: i }}));
            if(phaseData.enemies) phaseData.enemies.forEach(e => drawList.push({{ type: 'enemy', y: e.y, data: e }}));
            drawList.push({{ type: 'player', y: player.y }});
            drawList.push({{ type: 'ball', y: ball.y }});
            drawList.sort((a, b) => a.y - b.y);

            drawList.forEach(obj => {{
                let s = getScale(obj.y);
                if (obj.type === 'gate') {{
                    let idA = `p${{currentPhase}}g${{obj.index}}a`, idB = `p${{currentPhase}}g${{obj.index}}b`;
                    ctx.fillStyle = fallenCones.includes(idA) ? "rgba(255,100,0,0.3)" : "#ff6600";
                    if(fallenCones.includes(idA)) {{ ctx.beginPath(); ctx.ellipse(obj.data.x1, obj.data.y, 14*s, 5*s, 0, 0, Math.PI*2); ctx.fill(); }}
                    else {{ ctx.beginPath(); ctx.moveTo(obj.data.x1-8*s, obj.data.y); ctx.lineTo(obj.data.x1+8*s, obj.data.y); ctx.lineTo(obj.data.x1, obj.data.y-22*s); ctx.fill(); }}
                    ctx.fillStyle = fallenCones.includes(idB) ? "rgba(255,100,0,0.3)" : "#ff6600";
                    if(fallenCones.includes(idB)) {{ ctx.beginPath(); ctx.ellipse(obj.data.x2, obj.data.y, 14*s, 5*s, 0, 0, Math.PI*2); ctx.fill(); }}
                    else {{ ctx.beginPath(); ctx.moveTo(obj.data.x2-8*s, obj.data.y); ctx.lineTo(obj.data.x2+8*s, obj.data.y); ctx.lineTo(obj.data.x2, obj.data.y-22*s); ctx.fill(); }}
                }} else if (obj.type === 'enemy') {{
                    ctx.fillStyle="#f00"; ctx.fillRect(obj.data.x-9*s, obj.data.y-28*s, 18*s, 22*s);
                }} else if (obj.type === 'player') {{
                    let isHit = player.hitTimer > 0 && Math.floor(Date.now() / 80) % 2 === 0;
                    ctx.fillStyle = isHit ? "#ff0000" : "#ffd700";
                    ctx.fillRect(player.x-8*s, player.y-30*s, 16*s, 25*s);
                    ctx.fillStyle="#d2b48c"; ctx.beginPath(); ctx.arc(player.x, player.y-35*s, 7*s, 0, Math.PI*2); ctx.fill();
                }} else if (obj.type === 'ball') {{
                    ctx.fillStyle="white"; ctx.beginPath(); ctx.arc(ball.x, ball.y, 6*s, 0, Math.PI*2); ctx.fill();
                }}
            }});

            if(gameState === 'COUNTDOWN') {{
                ctx.fillStyle = "rgba(0,0,0,0.85)"; ctx.fillRect(0,0,320,460);
                ctx.fillStyle = "#ffd700"; ctx.font = "bold 50px monospace"; ctx.textAlign = "center";
                ctx.fillText(countdown, 160, 230);
            }}

            if(gameState === 'FINISHED') {{
                ctx.fillStyle = "rgba(0,0,0,0.96)"; ctx.fillRect(0,0,320,460);
                ctx.fillStyle = "#ffd700"; ctx.font = "bold 20px monospace"; ctx.textAlign = "center";
                ctx.fillText("RESUMO DE EVOLUÇÃO", 160, 140);
                let fs = Math.floor(score);
                ctx.font = "16px monospace"; ctx.fillText("SCORE FINAL: " + fs, 160, 170);
                
                if(fs >= 850) {{
                    ctx.fillStyle = "#0f0"; ctx.fillText("NÍVEL Z (ELITE)", 160, 210);
                    ctx.font = "12px monospace"; 
                    ctx.fillText("+2.5 {', '.join(DNA_ATTRS)}", 160, 240);
                    ctx.fillStyle = "#f44"; ctx.fillText("-1.5 {', '.join(TRAVA_ATTRS)}", 160, 260);
                }} else if(fs >= 500) {{
                    ctx.fillStyle = "#ffd700"; ctx.fillText("NÍVEL Y (TREINO)", 160, 210);
                    ctx.font = "12px monospace"; 
                    ctx.fillText("+1.0 {', '.join(DNA_ATTRS)}", 160, 240);
                    ctx.fillStyle = "#f44"; ctx.fillText("-1.0 {', '.join(TRAVA_ATTRS)}", 160, 260);
                }} else {{
                    ctx.fillStyle = "#f00"; ctx.fillText("NÍVEL X (ABAIXO)", 160, 210);
                    ctx.font = "12px monospace"; ctx.fillText("SEM EVOLUÇÃO NESTA SESSÃO", 160, 240);
                }}
            }}

            ctx.beginPath(); ctx.arc(joy.x, joy.y, 45, 0, Math.PI*2); ctx.strokeStyle='#ffd700'; ctx.stroke();
            ctx.beginPath(); ctx.arc(joy.currX, joy.currY, 20, 0, Math.PI*2); ctx.fillStyle='#ffd700'; ctx.fill();
        }}

        canvas.addEventListener('pointerdown', e => {{ 
            const r=canvas.getBoundingClientRect(); 
            if(Math.hypot(e.clientX-r.left-joy.x, e.clientY-r.top-joy.y)<60) {{ 
                joy.active=true; 
                if(audioCtx.state === 'suspended') audioCtx.resume(); 
            }} 
        }});
        canvas.addEventListener('pointermove', e => {{ if(!joy.active) return; const r=canvas.getBoundingClientRect(); let dx=e.clientX-r.left-joy.x, dy=e.clientY-r.top-joy.y, d=Math.min(Math.hypot(dx,dy),45), a=Math.atan2(dy,dx); joy.currX=joy.x+Math.cos(a)*d; joy.currY=joy.y+Math.sin(a)*d; }});
        canvas.addEventListener('pointerup', () => {{ joy.active=false; joy.currX=joy.x; joy.currY=joy.y; }});
        
        initModule(1);
        update();
    </script>
    """
    components.html(game_code, height=650)
    
    if st.button("VOLTAR AO LOBBY", use_container_width=True):
        st.session_state.app_mode = 'LOBBY'
        st.rerun()

st.sidebar.caption("GOAT TV FEDERATION © 2026")
