const steps = [
  ['WhatsApp received', 'Twilio · inbound', 'wa', 'complete'],
  ['Understand request', 'GPT-4o mini · 0.93 confidence', 'ai', 'complete'],
  ['Route conversation', 'Intent: booking', 'route', 'complete'],
  ['Call customer', 'Vapi · outbound', 'call', 'complete'],
  ['Sync reservation', 'HubSpot · deal update', 'sync', 'retry'],
  ['Confirm by message', 'Twilio · WhatsApp reply', 'send', 'active'],
];

function icon(type) {
  const icons = { wa:'◔', ai:'✦', route:'⌘', call:'⌕', sync:'▣', send:'↗' };
  return `<span class="step-icon ${type}">${icons[type]}</span>`;
}

document.querySelector('#app').innerHTML = `
  <main>
    <nav class="topbar">
      <a class="brand" href="#"><span class="brand-mark">S</span>signalflow</a>
      <div class="crumb"><span>Operations</span><b>/</b><span>Automations</span><b>/</b><strong>Execution #2231</strong></div>
      <div class="nav-actions"><button class="ghost">⌘ K</button><button class="avatar">AM</button></div>
    </nav>
    <section class="page-head">
      <div class="back">← &nbsp;All executions</div>
      <div class="head-row">
        <div><div class="eyebrow">PRODUCTION · COMPLETED 2 MIN AGO</div><h1>Appointment booking <span class="status">● Successful</span></h1><p>WhatsApp intake → voice agent → CRM confirmation</p></div>
        <div class="head-actions"><button class="secondary">↗ Share</button><button class="primary" id="rerun">↻ Run again</button></div>
      </div>
    </section>
    <section class="metrics">
      <div><label>RUN TIME</label><strong>6.4<span>s</span></strong><small>Fastest 15% this week</small></div>
      <div><label>STEPS COMPLETED</label><strong>6<span>/6</span></strong><small class="green">No dropped events</small></div>
      <div><label>RETRIES</label><strong class="purple">1</strong><small>CRM request recovered</small></div>
      <div><label>HUMAN HANDOFF</label><strong class="green">0<span> min</span></strong><small>Fully automated</small></div>
    </section>
    <section class="content-grid">
      <div class="panel journey">
        <div class="panel-head"><div><h2>Execution journey</h2><p>6 steps completed successfully</p></div><button class="view-toggle">⌁ &nbsp;Timeline</button></div>
        <div class="timeline">
          ${steps.map((s,i) => `<article class="step ${s[3]}" style="--i:${i}"><div class="rail">${icon(s[2])}</div><div class="step-content"><div><h3>${s[0]} ${s[3] === 'retry' ? '<span class="badge retry-badge">Recovered after retry</span>' : s[3] === 'active' ? '<span class="badge sent-badge">Sent</span>' : ''}</h3><p>${s[1]}</p></div><div class="time">${['02:09:31','02:09:32','02:09:33','02:09:37','02:09:43','02:09:44'][i]}<span>${i === 4 ? '1.9s' : i === 3 ? '4.0s' : '0.2s'}</span></div></div></article>`).join('')}
        </div>
      </div>
      <aside class="right-col">
        <section class="panel outcome"><div class="spark">✦</div><div class="eyebrow">FINAL OUTCOME</div><h2>Booking confirmed</h2><p>Thursday, 2:00 PM</p><hr><div class="person"><span>AA</span><div><strong>Alex Adebayo</strong><small>+234 802 555 0118</small></div><button>↗</button></div></section>
        <section class="panel recent"><div class="panel-head"><div><h2>Recent runs</h2><p>Same workflow · last 24h</p></div><button>View all</button></div>
          <div class="run"><i class="dot green-dot"></i><span>Appointment booking</span><small>now</small></div>
          <div class="run"><i class="dot"></i><span>CRM update</span><small>2m</small></div>
          <div class="run"><i class="dot purple-dot"></i><span>Voice booking</span><small>14m</small></div>
        </section>
      </aside>
    </section>
    <section class="panel activity"><div class="panel-head"><div><h2>Activity log</h2><p>Detailed event history</p></div><button class="filter">⌄ All events</button></div>
      <div class="logs"><p><time>02:09:31.028</time><b class="tag blue">VAPI</b> Call connected. <em>Agent: Nora</em></p><p><time>02:09:43.534</time><b class="tag red">CRM</b> Deal update timed out after 8000ms</p><p><time>02:09:51.922</time><b class="tag purpletag">RETRY</b> Retry 2/3 · backoff 1.2s</p><p><time>02:09:56.432</time><b class="tag green-tag">DONE</b> Reservation marked confirmed in HubSpot</p></div>
    </section>
  </main>`;

document.querySelector('#rerun').addEventListener('click', e => { e.currentTarget.textContent = '✓ Queued'; e.currentTarget.classList.add('queued'); setTimeout(() => { e.currentTarget.textContent = '↻ Run again'; e.currentTarget.classList.remove('queued') }, 1800) });
