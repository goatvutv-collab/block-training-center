import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="GOAT TV - CT v19.2", layout="centered", initial_sidebar_state="collapsed")

DNA_ATTRS = ["Condução", "Velocidade", "Drible"]
TRAVA_ATTRS = ["Desarme", "Impacto Físico"]

if 'app_mode' not in st.session_state: st.session_state.app_mode = 'LOBBY'

if st.session_state.app_mode == 'LOBBY':
    st.markdown("<h2 style='text-align: center; color: #ffd700;'>🏟️ LOBBY GOAT TV</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.2])
    with col1:
        tipo_treino = st.selectbox("SETOR:", ["DRIBLE", "PASSE", "CHUTE"])
        if st.button("INICIAR TREINO 🏟️", use_container_width=True):
            st.session_state.tipo_selecionado = tipo_treino
            st.session_state.app_mode = 'TRAINING'; st.rerun()
    with col2:
        st.markdown("### 📊 Evolução")
        st.success("📈 DNA: " + ", ".join(DNA_ATTRS))
        st.error("📉 TRAVA: " + ", ".join(TRAVA_ATTRS))
        st.info("💡 UI Atualizada: HUD e Setas maiores para mobile!")

elif st.session_state.app_mode == 'TRAINING':
    tipo = st.session_state.tipo_selecionado
    game_code = f"""
    <div style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
        <div id="hud" style="color: white; font-family: monospace; margin-bottom: 8px; font-size: 14px; background: #000; padding: 12px 20px; border: 2px solid #ffd700; border-radius: 12px; width: 320px; display: flex; justify-content: space-between; box-sizing: border-box;">
            <span>ETAPA: <b id="phaseDisp" style="color: #0f0;">1/4</b></span>
            <span>SCORE: <b id="scoreDisp" style="color: #0f0;">1000</b></span>
        </div>
        <canvas id="gameCanvas" width="320" height="600" style="background: #111; border: 4px solid #333; border-radius: 10px; touch-action: none;"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas'); const ctx = canvas.getContext('2d');
        const scoreDisp = document.getElementById('scoreDisp'); const phaseDisp = document.getElementById('phaseDisp');
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

        function playSound(f, d=0.1) {{
            const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
            o.type = 'triangle'; o.frequency.setValueAtTime(f, audioCtx.currentTime);
            g.gain.setValueAtTime(0.1, audioCtx.currentTime); o.connect(g); g.connect(audioCtx.destination);
            o.start(); o.stop(audioCtx.currentTime + d);
        }}

        let player = {{ x: 160, y: 410, speed: 1.5, hitTimer: 0, juggleY: 0 }};
        let ball = {{ x: 160, y: 385 }}; let score = 1000; let currentPhase = 1;
        let currentGate = 0; let direction = 1; let gameState = 'COUNTDOWN'; let countdown = 3;
        let fallenCones = []; let scoreM123 = 0;

        // RHYTHM
        let rhythmNotes = []; let rhythmTimer = 0; let missedAny = false; let hits = 0;

        const phases = {{
            1: {{ startPos:{{x:160, y:410}}, gates:[{{x1:60,x2:120,y:320}},{{x1:60,x2:120,y:150}},{{x1:200,x2:260,y:150}},{{x1:200,x2:260,y:320}}], enemies:[] }},
            2: {{ startPos:{{x:160, y:410}}, gates:[{{x1:40,x2:100,y:350}},{{x1:220,x2:280,y:250}},{{x1:40,x2:100,y:150}},{{x1:130,x2:190,y:80}}], enemies:[] }},
            3: {{ startPos:{{x:160, y:410}}, gates:[{{x1:220,x2:280,y:380}},{{x1:40,x2:100,y:300}},{{x1:220,x2:280,y:220}},{{x1:40,x2:100,y:140}},{{x1:130,x2:190,y:60}}], 
                enemies:[{{x:100,y:340,cx:100,cy:340,rx:120,ry:0,sx:1.5,sy:0,dx:1,dy:0,t:'H'}},{{x:220,y:340,cx:220,cy:340,rx:120,ry:0,sx:1.5,sy:0,dx:-1,dy:0,t:'H'}},
                         {{x:160,y:180,cx:160,cy:180,rx:90,ry:45,sx:1.3,sy:0.8,dx:1,dy:1,t:'D'}},{{x:160,y:100,cx:160,cy:100,rx:90,ry:35,sx:1.3,sy:0.6,dx:-1,dy:-1,t:'D'}}] }},
            4: {{ startPos:{{x:160, y:300}}, isRhythm: true }}
        }};

        const joy = {{ x: 160, y: 520, r: 50, currX: 160, currY: 520, active: false }};
        const rBtns = [{{x:55,y:520,d:'L'}}, {{x:125,y:490,d:'U'}}, {{x:195,y:490,d:'D'}}, {{x:265,y:520,d:'R'}}];

        function drawArrow(x, y, dir, color, size=15) {{
            ctx.save(); ctx.translate(x, y);
            if(dir==='R') ctx.rotate(Math.PI/2); else if(dir==='D') ctx.rotate(Math.PI); else if(dir==='L') ctx.rotate(-Math.PI/2);
            ctx.beginPath(); ctx.moveTo(0, -size); ctx.lineTo(size, size/2); ctx.lineTo(-size, size/2); ctx.closePath();
            ctx.fillStyle = color; ctx.fill(); ctx.restore();
        }}

        function initModule(p) {{
            gameState = 'COUNTDOWN'; countdown = 3; currentPhase = p;
            const c = phases[p]; player.x = c.startPos.x; player.y = c.startPos.y;
            ball.x = player.x; ball.y = player.y - 25; currentGate = 0; direction = 1; fallenCones = [];
            if(p === 4) {{ rhythmTimer = 0; rhythmNotes = []; missedAny = false; hits = 0; }}
            let t = setInterval(() => {{ countdown--; if(countdown <= 0) {{ clearInterval(t); gameState = 'PLAYING'; }} }}, 1000);
        }}

        function spawnNote() {{
            rhythmNotes.push({{ x: 340, type: Math.floor(Math.random()*4), speed: rhythmTimer < 30 ? 4 : 7 }});
        }}

        function update() {{
            if (gameState === 'FINISHED') return;
            if (player.hitTimer > 0) player.hitTimer--;
            if (gameState === 'PLAYING') {{
                if (currentPhase < 4) {{
                    if (joy.active) {{
                        let dx = joy.currX - joy.x, dy = joy.currY - joy.y, d = Math.hypot(dx, dy);
                        if (d > 3) {{ 
                            let vx = (dx/d)*player.speed, vy = (dy/d)*player.speed;
                            let margin = 20 * (player.y/460*0.55+0.45);
                            if(player.x+vx > margin && player.x+vx < 320-margin) player.x += vx;
                            if(player.y+vy > 10 && player.y+vy < 450) player.y += vy;
                            ball.x += (player.x - ball.x) * 0.25; ball.y += (player.y - 22*(player.y/460*0.55+0.45) - ball.y) * 0.25;
                        }}
                    }}
                    let pd = phases[currentPhase];
                    if(pd.enemies) pd.enemies.forEach(e => {{
                        e.x += e.sx*e.dx; e.y += e.sy*e.dy;
                        if(Math.abs(e.x-e.cx)>e.rx/2) e.dx*=-1; if(e.t==='D'&&Math.abs(e.y-e.cy)>e.ry/2) e.dy*=-1;
                        if(Math.hypot(player.x-e.x, player.y-e.y)<18) {{ score-=0.8; player.hitTimer=10; if (navigator.vibrate) navigator.vibrate(40); }}
                    }});
                    pd.gates.forEach((g, i) => {{
                        let idA = `p${{currentPhase}}g${{i}}a`, idB = `p${{currentPhase}}g${{i}}b`;
                        if(!fallenCones.includes(idA) && Math.hypot(player.x-g.x1, player.y-g.y)<12) {{ fallenCones.push(idA); score-=50; playSound(800); }}
                        if(!fallenCones.includes(idB) && Math.hypot(player.x-g.x2, player.y-g.y)<12) {{ fallenCones.push(idB); score-=50; playSound(800); }}
                    }});
                    let g = pd.gates[currentGate];
                    if (Math.hypot(ball.x-(g.x1+g.x2)/2, ball.y-g.y)<25) {{
                        currentGate += direction;
                        if(currentGate >= pd.gates.length) {{ direction=-1; currentGate=pd.gates.length-2; }}
                        else if(currentGate < 0) {{ if(currentPhase===3) scoreM123 = score; initModule(currentPhase + 1); }}
                    }}
                }} else {{ // MODULO 4
                    rhythmTimer += 1/60; if(rhythmTimer >= 60) gameState = 'FINISHED';
                    if(Math.floor(rhythmTimer*60) % (rhythmTimer < 30 ? 45 : 25) === 0) spawnNote();
                    rhythmNotes.forEach((n, i) => {{
                        n.x -= n.speed;
                        if(n.x < -20) {{ rhythmNotes.splice(i, 1); score -= 15; missedAny = true; playSound(300); }}
                    }});
                    if(player.juggleY > 0) player.juggleY -= 2;
                }}
            }}
            scoreDisp.innerText = Math.floor(score); phaseDisp.innerText = currentPhase + "/4";
            render(); requestAnimationFrame(update);
        }}

        function render() {{
            ctx.fillStyle = '#1e3d1a'; ctx.fillRect(0,0,320,460);
            ctx.fillStyle = '#050505'; ctx.fillRect(0,460,320,140);
            if(currentPhase < 4) {{
                ctx.strokeStyle = "rgba(255,255,255,0.08)";
                for(let i=-100; i<=420; i+=40) {{ ctx.beginPath(); ctx.moveTo(160, -80); ctx.lineTo(i*1.5-80, 460); ctx.stroke(); }}
                let pd = phases[currentPhase];
                pd.gates.forEach((g, i) => {{
                    let s = (g.y/460*0.55+0.45); let idA = `p${{currentPhase}}g${{i}}a`;
                    ctx.fillStyle = fallenCones.includes(idA) ? "rgba(255,100,0,0.3)" : "#ff6600";
                    ctx.beginPath(); ctx.ellipse(g.x1, g.y, 14*s, 5*s, 0, 0, Math.PI*2); ctx.fill();
                    if(i===currentGate && gameState==='PLAYING') {{ ctx.strokeStyle=direction===1?"#ffd700":"#0f0"; ctx.strokeRect(g.x1, g.y-20, g.x2-g.x1, 2); }}
                }});
                ctx.fillStyle = player.hitTimer > 0 && Math.floor(Date.now()/80)%2===0 ? "#f00" : "#ffd700";
                ctx.fillRect(player.x-8, player.y-30, 16, 25);
                ctx.fillStyle="white"; ctx.beginPath(); ctx.arc(ball.x, ball.y, 6, 0, Math.PI*2); ctx.fill();
                ctx.beginPath(); ctx.arc(joy.x, joy.y, joy.r, 0, Math.PI*2); ctx.strokeStyle='#ffd700'; ctx.stroke();
                ctx.beginPath(); ctx.arc(joy.currX, joy.currY, 20, 0, Math.PI*2); ctx.fillStyle='#ffd700'; ctx.fill();
            }} else {{ 
                ctx.fillStyle="rgba(255,255,255,0.05)"; ctx.fillRect(0, 100, 320, 50);
                const dirs = ['L','U','D','R'];
                dirs.forEach((d, i) => drawArrow(35 + i*20, 125, d, "rgba(255,255,255,0.2)", 10));
                rhythmNotes.forEach(n => drawArrow(n.x, 125, dirs[n.type], "#0f0", 15));
                ctx.fillStyle="#ffd700"; ctx.fillRect(150, 350, 8, 40); ctx.fillRect(162, 350, 8, 40);
                ctx.fillStyle="white"; ctx.beginPath(); ctx.arc(160, 340 - player.juggleY, 10, 0, Math.PI*2); ctx.fill();
                rBtns.forEach((b, i) => {{
                    ctx.beginPath(); ctx.arc(b.x, b.y, 35, 0, Math.PI*2); ctx.strokeStyle="#ffd700"; ctx.lineWidth=2; ctx.stroke();
                    drawArrow(b.x, b.y, dirs[i], "#fff", 15);
                }});
            }}
            if(gameState === 'COUNTDOWN') {{ ctx.fillStyle="rgba(0,0,0,0.85)"; ctx.fillRect(0,0,320,460); ctx.fillStyle="#ffd700"; ctx.font="bold 50px monospace"; ctx.textAlign="center"; ctx.fillText(countdown, 160, 230); }}
            if(gameState === 'FINISHED') {{
                ctx.fillStyle="rgba(0,0,0,0.96)"; ctx.fillRect(0,0,320,460); ctx.fillStyle="#ffd700"; ctx.textAlign="center";
                ctx.font="bold 18px monospace"; ctx.fillText("RESUMO FINAL", 160, 140);
                let fs = Math.floor(score); ctx.fillText("SCORE FINAL: " + fs, 160, 175);
                if(fs >= 950) {{ ctx.fillStyle="#0f0"; ctx.fillText("NÍVEL Z (ELITE)", 160, 215); ctx.font="11px monospace"; ctx.fillText("+2.5 DNA", 160, 245); ctx.fillStyle="#f44"; ctx.fillText("-1.5 TRAVA", 160, 265); }}
                else if(fs >= 600) {{ ctx.fillStyle="#ffd700"; ctx.fillText("NÍVEL Y (TREINO)", 160, 215); ctx.font="11px monospace"; ctx.fillText("+1.0 DNA", 160, 245); ctx.fillStyle="#f44"; ctx.fillText("-1.0 TRAVA", 160, 265); }}
                else {{ ctx.fillStyle="#f00"; ctx.fillText("NÍVEL X (ABAIXO)", 160, 215); ctx.font="11px monospace"; ctx.fillText("SEM EVOLUÇÃO", 160, 245); }}
                if(!missedAny && hits > 0) {{ ctx.fillStyle="#fff"; ctx.font="bold 12px monospace"; ctx.fillText("GABARITO RÍTMICO: +1.0 EXTRA!", 160, 290); }}
            }}
        }}

        canvas.addEventListener('pointerdown', e => {{
            const r=canvas.getBoundingClientRect(); const x=e.clientX-r.left, y=e.clientY-r.top;
            if(audioCtx.state === 'suspended') audioCtx.resume();
            if(currentPhase < 4) {{ if(Math.hypot(x-joy.x, y-joy.y)<65) joy.active=true; }}
            else {{
                rBtns.forEach((b, i) => {{
                    if(Math.hypot(x-b.x, y-b.y)<40) {{
                        let h = false;
                        rhythmNotes.forEach((n, ni) => {{
                            if(n.type === i && n.x > 15 && n.x < 85) {{
                                h = true; rhythmNotes.splice(ni, 1); hits++;
                                let pts = rhythmTimer < 30 ? 20 : 50;
                                score += pts; player.juggleY = 50; playSound(1000, 0.05); if(navigator.vibrate) navigator.vibrate(30);
                            }}
                        }});
                        if(!h) {{ score -= 10; missedAny = true; playSound(400); }}
                    }}
                }});
            }}
        }});
        canvas.addEventListener('pointermove', e => {{ if(!joy.active) return; const r=canvas.getBoundingClientRect(); let dx=e.clientX-r.left-joy.x, dy=e.clientY-r.top-joy.y, d=Math.min(Math.hypot(dx,dy),50), a=Math.atan2(dy,dx); joy.currX=joy.x+Math.cos(a)*d; joy.currY=joy.y+Math.sin(a)*d; }});
        canvas.addEventListener('pointerup', () => {{ joy.active=false; joy.currX=joy.x; joy.currY=joy.y; }});
        initModule(1); update();
    </script>
    """
    components.html(game_code, height=660)
    if st.button("VOLTAR AO LOBBY", use_container_width=True):
        st.session_state.app_mode = 'LOBBY'; st.rerun()

st.sidebar.caption("GOAT TV FEDERATION © 2026")
