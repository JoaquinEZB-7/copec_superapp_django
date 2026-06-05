  const vp = document.getElementById('viewport');
  const PRECIO_93 = 1149;
  let cargaTimer = null;

  function clpUI(n){
    return Math.round(n).toLocaleString('es-CL');
  }

  function dec1UI(n){
    return n.toFixed(1).replace('.', ',');
  }

  function detenerCargaSimulada(){
    if(cargaTimer){
      clearInterval(cargaTimer);
      cargaTimer = null;
    }
  }

  function iniciarCargaSimulada(){
    const screen = document.getElementById('cargando');
    if(!screen) return;

    detenerCargaSimulada();

    const litrosEl = document.getElementById('litros-actuales');
    const montoEl = document.getElementById('monto-actual');
    const progresoEl = document.getElementById('charge-progress');
    const hintEl = document.getElementById('charge-hint');
    const summaryEl = document.getElementById('charge-summary');
    const saldoAntesEl = document.getElementById('saldo-antes');
    const descuentoEl = document.getElementById('descuento-pay');
    const saldoDespuesEl = document.getElementById('saldo-despues');
    const puntosGanadosEl = document.getElementById('puntos-ganados');
    const puntosTotalEl = document.getElementById('puntos-total');
    const finalTextEl = document.getElementById('charge-final-text');

    const saldoInicial = Number(screen.dataset.saldoInicial || 0);
    const puntosIniciales = Number(screen.dataset.puntosInicial || 0);
    const objetivoLitros = 28.4;
    const incremento = 0.4;
    const descuentoRate = 0.08;
    const puntosPorMonto = 1000;

    let litros = 0;
    let montosinDescuento = 0;

    litrosEl.textContent = '0,0';
    montoEl.textContent = '$0';
    progresoEl.style.width = '0%';
    hintEl.textContent = 'Autorizando surtidor y abriendo flujo de carga...';
    summaryEl.hidden = true;

    cargaTimer = setInterval(() => {
      litros = Math.min(objetivoLitros, litros + incremento);
      montosinDescuento = litros * PRECIO_93;
      const montoFinal = Math.round(montosinDescuento * (1 - descuentoRate));
      const puntosNuevos = Math.floor(montoFinal / puntosPorMonto);
      const progreso = (litros / objetivoLitros) * 100;

      litrosEl.textContent = dec1UI(litros);
      montoEl.textContent = '$' + clpUI(montoFinal);
      progresoEl.style.width = `${Math.min(100, progreso)}%`;

      if(litros < objetivoLitros){
        hintEl.textContent = `Surtiendo combustible: ${dec1UI(litros)} L · ${'$' + clpUI(montoFinal)} estimados`;
        return;
      }

      detenerCargaSimulada();
      const descuento = montosinDescuento - montoFinal;
      const saldoFinal = saldoInicial - montoFinal;
      const puntosFinales = puntosIniciales + puntosNuevos;

      hintEl.textContent = 'Proceso completado en el surtidor seleccionado.';
      summaryEl.hidden = false;
      saldoAntesEl.textContent = '$' + clpUI(saldoInicial);
      descuentoEl.textContent = '-$' + clpUI(descuento);
      saldoDespuesEl.textContent = '$' + clpUI(saldoFinal);
      puntosGanadosEl.textContent = `+${clpUI(puntosNuevos)} pts`;
      puntosTotalEl.textContent = `Total: ${clpUI(puntosFinales)} pts`;
      finalTextEl.textContent = `Se registraron ${dec1UI(objetivoLitros)} L, con descuento Copec Pay de -$${clpUI(descuento)} y saldo visual final de $${clpUI(saldoFinal)}.`;
    }, 420);
  }

  function onScreenChange(next){
    if(next && next.id === 'cargando'){
      iniciarCargaSimulada();
      return;
    }
    detenerCargaSimulada();
  }

  function go(id){
    const cur = vp.querySelector('.screen.active');
    const next = document.getElementById(id);
    if(cur===next) return;
    if(cur){ cur.classList.remove('active'); cur.classList.add('exit-left'); }
    next.classList.remove('exit-left');
    next.style.transition='none'; next.style.transform='translateX(100%)';
    requestAnimationFrame(()=>{ next.style.transition=''; next.classList.add('active'); next.style.transform=''; });
    setTimeout(()=>{ if(cur) cur.classList.remove('exit-left'); },450);
    next.scrollTop = 0;
    const navTarget = next.dataset.nav;
    document.querySelectorAll('.navbtn').forEach(b=>{
      b.classList.toggle('on', !!navTarget && b.dataset.target===navTarget);
    });
    onScreenChange(next);
  }

  // El cálculo del viaje se hace EN EL BACKEND (Django) usando los datos reales del vehículo.
  async function pickDest(btn){
    document.querySelectorAll('#destbtns button').forEach(b=>b.classList.remove('sel'));
    btn.classList.add('sel');
    document.getElementById('dest').value = btn.dataset.name;
    const r = await fetch(`${VIAJE_API}?destino=${btn.dataset.id}`);
    const d = await r.json();
    document.getElementById('ekm').textContent = d.km;
    document.getElementById('elt').textContent = d.litros;
    document.getElementById('ecl').textContent = d.costo;
    document.getElementById('etip').innerHTML = d.tip;
    const cont = document.getElementById('stops'); cont.innerHTML='';
    d.estaciones.forEach(s=>{
      cont.innerHTML += `<div class="routestop"><span class="km">${s.km}</span><div style="flex:1"><h6 style="font-size:13.5px;font-weight:700">${s.nombre}</h6><span style="font-size:11px;color:var(--muted)">${s.servicios}</span></div><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6A748C" stroke-width="2"><path d="M9 6l6 6-6 6"/></svg></div>`;
    });
    document.getElementById('est').classList.add('show');
  }