(function(){
  'use strict';
  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function store(k, v){ try{ if(v===undefined) return localStorage.getItem(k); localStorage.setItem(k,v);}catch(e){ return null; } }
  // Run a DOM change inside a view transition when the browser supports it.
  function morph(fn){
    if(document.startViewTransition && !reduce){ document.startViewTransition(fn); } else { fn(); }
  }

  /* ================================================================
     GLOBAL (runs once; survives page swaps)
     ================================================================ */

  /* ---------------- tidbit tooltip ---------------- */
  var tip = document.createElement('div');
  tip.className = 'tip'; tip.setAttribute('aria-hidden','true');
  document.body.appendChild(tip);
  var tipTimer;
  function placeTip(x, y){
    var w = tip.offsetWidth, h = tip.offsetHeight, pad = 12;
    var left = Math.min(Math.max(pad, x + 16), window.innerWidth - w - pad);
    var top = y + 22;
    if(top + h > window.innerHeight - pad) top = y - h - 16;
    tip.style.left = left + 'px'; tip.style.top = top + 'px';
  }
  function showTip(el, x, y){
    var text = el.getAttribute('data-tip'); if(!text) return;
    tip.textContent = text; tip.classList.add('on'); placeTip(x, y);
  }
  function hideTip(){ tip.classList.remove('on'); }
  document.addEventListener('pointerover', function(e){
    if(e.pointerType === 'touch') return;
    var el = e.target.closest('[data-tip]'); if(el) showTip(el, e.clientX, e.clientY);
  });
  document.addEventListener('pointermove', function(e){
    if(e.pointerType === 'touch') return;
    var el = e.target.closest('[data-tip]');
    if(el){ if(!tip.classList.contains('on')) showTip(el, e.clientX, e.clientY); else placeTip(e.clientX, e.clientY); }
    else hideTip();
  });
  document.addEventListener('pointerout', function(e){
    if(!e.relatedTarget || !e.relatedTarget.closest || !e.relatedTarget.closest('[data-tip]')) hideTip();
  });
  document.addEventListener('focusin', function(e){
    var el = e.target.closest && e.target.closest('[data-tip]'); if(!el || !el.matches(':focus-visible')) return;
    var r = el.getBoundingClientRect(); showTip(el, r.left + r.width/2 - 60, r.bottom - 30);
  });
  document.addEventListener('focusout', hideTip);
  document.addEventListener('pointerdown', function(e){
    if(e.pointerType !== 'touch') return;
    var el = e.target.closest('[data-tip]');
    if(el && !el.matches('a,button')){
      showTip(el, e.clientX - 40, e.clientY - 70);
      clearTimeout(tipTimer); tipTimer = setTimeout(hideTip, 3200);
    } else hideTip();
  });
  window.addEventListener('scroll', hideTip, {passive:true});

  /* ---------------- home tab filter (live DOM queries so it works after swaps) ---------------- */
  var tabNames = {all:'all', about:'about', work:'work', 'side-quests':'side'};
  function applyTab(name){
    document.querySelectorAll('[data-tab]').forEach(function(t){ t.setAttribute('aria-selected', t.dataset.tab === name); });
    var key = tabNames[name] || 'all';
    document.querySelectorAll('.bento .tile').forEach(function(t){
      t.hidden = (t.getAttribute('data-in') || '').split(' ').indexOf(key) === -1;
    });
  }
  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape'){ var lb = document.getElementById('lightbox'); if(lb) lb.classList.remove('on'); }
  });

  /* ---------------- audio guide: lives OUTSIDE #page, so it is never reloaded ---------------- */
  var agPlaying = false;
  function syncPlayTile(){ var pt = document.getElementById('playTile'); if(pt) pt.classList.toggle('playing', agPlaying); }
  var widget = document.getElementById('audioGuide');
  if(widget){
    var toggle = document.getElementById('agToggle'), closeBtn = document.getElementById('agClose');
    var panel = document.getElementById('agPanel'), frameEl = document.getElementById('agFrame');
    var atabs = widget.querySelectorAll('.audio-tab'); var KEY = 'jb_portfolio_audio_state';
    var controller = null, saveTimer = null, pendingMount = null;
    function read(){ try{ return JSON.parse(localStorage.getItem(KEY)) || null; }catch(e){ return null; } }
    function write(p){ try{ localStorage.setItem(KEY, JSON.stringify(Object.assign(read() || {}, p))); }catch(e){} }
    function markTab(uri){ atabs.forEach(function(t){ t.classList.toggle('active', t.dataset.uri === uri); }); }
    function mount(uri, resume, autoplay){
      if(!window.SpotifyIframeApi){ pendingMount = [uri, resume, autoplay]; return; }
      window.SpotifyIframeApi.createController(frameEl, {uri: uri}, function(c){
        controller = c;
        c.addListener('playback_update', function(e){
          var d = e.data || {}; clearTimeout(saveTimer);
          saveTimer = setTimeout(function(){ write({uri: uri, position: d.position || 0, paused: !!d.isPaused, savedAt: Date.now()}); }, 250);
          agPlaying = !d.isPaused; syncPlayTile();
        });
        c.addListener('ready', function(){ if(resume) c.seek(resume); if(autoplay) c.play(); });
      });
    }
    function load(tab, resume, autoplay){
      var uri = tab.dataset.uri; markTab(uri); write({uri: uri, position: resume || 0, paused: autoplay === false});
      if(controller){ controller.loadUri(uri); if(autoplay !== false) controller.play(); } else mount(uri, resume, autoplay !== false);
    }
    // Fallback only: if the browser does a full page load (e.g. opened from disk), resume where we left off.
    window.onSpotifyIframeApiReady = function(api){
      window.SpotifyIframeApi = api;
      if(pendingMount){ var pm = pendingMount; pendingMount = null; mount(pm[0], pm[1], pm[2]); return; }
      var s = read();
      if(s && s.uri){
        markTab(s.uri); mount(s.uri, s.position, false);
        if(s.open){ widget.classList.add('open'); requestAnimationFrame(function(){ panel.classList.add('show'); }); }
      }
    };
    toggle.addEventListener('click', function(){
      var opening = !widget.classList.contains('open');
      widget.classList.toggle('open'); write({open: opening});
      if(opening && !controller) load(atabs[0], 0, true);
      if(opening) requestAnimationFrame(function(){ panel.classList.add('show'); }); else panel.classList.remove('show');
    });
    closeBtn.addEventListener('click', function(e){ e.stopPropagation(); widget.classList.remove('open'); panel.classList.remove('show'); write({open:false}); });
    atabs.forEach(function(t){ t.addEventListener('click', function(){ load(t, 0, true); }); });
    var s = document.createElement('script'); s.src = 'https://open.spotify.com/embed/iframe-api/v1'; s.async = true; document.body.appendChild(s);
  }
  function openPlayer(){
    var w = document.getElementById('audioGuide'), t = document.getElementById('agToggle');
    if(t && w && !w.classList.contains('open')) t.click();
  }

  /* ================================================================
     PER-PAGE (runs on first load and after every in-place page swap)
     ================================================================ */
  function initPage(){
    /* theme buttons (one per view) */
    var themeBtns = document.querySelectorAll('.theme-btn');
    var paintTheme = function(){
      var dark = root.getAttribute('data-theme') === 'dark';
      themeBtns.forEach(function(b){ b.setAttribute('aria-pressed', dark); b.querySelector('.txt').textContent = dark ? 'Dark' : 'Light'; });
    };
    themeBtns.forEach(function(b){
      b.addEventListener('click', function(){
        var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', next); store('jb_theme', next); paintTheme();
      });
    });
    paintTheme();

    /* home tabs */
    var tabs = document.querySelectorAll('[data-tab]');
    if(tabs.length){
      tabs.forEach(function(t){
        t.addEventListener('click', function(){
          var name = t.dataset.tab;
          morph(function(){ applyTab(name); });
          history.replaceState(null, '', name === 'all' ? '#/' : '#' + name);
        });
      });
    }
    var playTile = document.getElementById('playTile');
    if(playTile){ playTile.addEventListener('click', openPlayer); syncPlayTile(); }

    /* ranked-list sheet */
    var sheet = document.getElementById('sheet');
    if(sheet){
      var LD = JSON.parse(document.getElementById('listData').textContent);
      var act = document.getElementById('sheetAct');
      var openSheet = function(key){
        var d = LD[key]; if(!d) return;
        document.getElementById('sheetIcon').innerHTML = d.icon;
        document.getElementById('sheetTitle').textContent = d.title;
        document.getElementById('sheetSub').textContent = d.sub || '';
        var ol = document.getElementById('sheetList'); ol.textContent = '';
        d.items.forEach(function(it){
          var li = document.createElement('li'); var box = document.createElement('div');
          var h = document.createElement('h4'); h.textContent = it.t; box.appendChild(h);
          if(it.n){ var p = document.createElement('p'); p.textContent = it.n; box.appendChild(p); }
          if(it.todo) li.className = 'todo';
          li.appendChild(box); ol.appendChild(li);
        });
        if(d.action){ act.hidden = false; act.textContent = d.action; } else act.hidden = true;
        hideTip(); sheet.showModal(); sheet.querySelector('.sheet-in').scrollTop = 0;
      };
      document.querySelectorAll('[data-list]').forEach(function(b){ b.addEventListener('click', function(){ openSheet(b.dataset.list); }); });
      document.getElementById('sheetX').addEventListener('click', function(){ sheet.close(); });
      sheet.addEventListener('click', function(e){ if(e.target === sheet) sheet.close(); });
      act.addEventListener('click', function(){ sheet.close(); openPlayer(); });
    }

    /* photo galleries (About fact tiles) */
    var gal = document.getElementById('gallery');
    if(gal){
      var GD = JSON.parse(document.getElementById('galleryData').textContent);
      var openGal = function(key){
        var d = GD[key]; if(!d || !d.items.length) return;
        document.getElementById('galTitle').textContent = d.title;
        document.getElementById('galSub').textContent = d.sub || '';
        var grid = document.getElementById('galGrid'); grid.textContent = '';
        d.items.forEach(function(it){
          var f = document.createElement('figure'); f.className = 'g-item';
          var im = document.createElement('img'); im.src = it.src; im.alt = it.alt || ''; im.loading = 'lazy'; f.appendChild(im);
          if(it.cap){ var c = document.createElement('figcaption'); c.textContent = it.cap; f.appendChild(c); }
          grid.appendChild(f);
        });
        hideTip(); gal.showModal(); gal.querySelector('.sheet-in').scrollTop = 0;
      };
      document.querySelectorAll('[data-gallery]').forEach(function(b){ b.addEventListener('click', function(){ openGal(b.dataset.gallery); }); });
      document.getElementById('galX').addEventListener('click', function(){ gal.close(); });
      gal.addEventListener('click', function(e){ if(e.target === gal) gal.close(); });
    }

    /* TL;DR / Detailed */
    var viewBtns = document.querySelectorAll('[data-view-btn]');
    var paintView = function(){
      var v = root.getAttribute('data-view');
      viewBtns.forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.viewBtn === v); });
    };
    var setView = function(v, keepScroll){
      morph(function(){
        root.setAttribute('data-view', v); store('jb_view', v); paintView();
        var main = document.querySelector('.cs'); if(main && !reduce){ main.classList.remove('fade-in'); void main.offsetWidth; main.classList.add('fade-in'); }
        if(!keepScroll){ var h = document.querySelector('.cs-title'); if(h && window.scrollY > h.offsetTop + h.offsetHeight) window.scrollTo(0, 0); }
      });
    };
    viewBtns.forEach(function(b){ b.addEventListener('click', function(){ setView(b.dataset.viewBtn); }); });
    document.querySelectorAll('[data-go-detail]').forEach(function(b){ b.addEventListener('click', function(){ setView('detail', true); }); });
    paintView();

    /* carousels */
    document.querySelectorAll('.car').forEach(function(car){
      var imgs = car.querySelectorAll('.frame img'); var i = 0;
      var cur = car.querySelector('[data-cur]'), tot = car.querySelector('[data-tot]');
      var pad = function(n){ return (n < 10 ? '0' : '') + n; };
      if(tot) tot.textContent = pad(imgs.length);
      var go = function(n){
        imgs[i].classList.remove('on'); i = (n + imgs.length) % imgs.length; imgs[i].classList.add('on');
        if(cur) cur.textContent = pad(i + 1);
      };
      car.querySelector('[data-prev]').addEventListener('click', function(){ go(i - 1); });
      car.querySelector('[data-next]').addEventListener('click', function(){ go(i + 1); });
      car.addEventListener('keydown', function(e){ if(e.key === 'ArrowLeft') go(i - 1); if(e.key === 'ArrowRight') go(i + 1); });
    });

    /* flip frames + lightbox */
    var lb = document.getElementById('lightbox');
    document.querySelectorAll('.frame-card').forEach(function(card){
      var flip = function(){ card.classList.toggle('flipped'); card.setAttribute('aria-pressed', card.classList.contains('flipped')); };
      card.addEventListener('click', function(e){ if(e.target.closest('.exp')) return; flip(); });
      card.addEventListener('keydown', function(e){ if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); flip(); } });
      var exp = card.querySelector('.exp');
      if(exp && lb){ exp.addEventListener('click', function(e){
        e.stopPropagation(); lb.querySelector('img').src = card.querySelector('.front img').src; lb.classList.add('on');
      }); }
    });
    document.querySelectorAll('[data-zoom]').forEach(function(el){
      el.addEventListener('click', function(){ var im = lb.querySelector('img'); im.src = el.dataset.zoom; im.alt = el.dataset.alt || ''; lb.classList.add('on'); });
    });
    if(lb && !lb.dataset.bound){ lb.dataset.bound = '1'; lb.addEventListener('click', function(){ lb.classList.remove('on'); }); }
  }

  /* ================================================================
     ROUTER: every page is a <div class="view"> inside this one document.
     Switching views only toggles `hidden`, so the document (and the Spotify
     player inside it) is never reloaded, even when opened straight from disk.
     ================================================================ */
  var ROUTES = {'/':'home','/serendipi-tea':'serendipi-tea','/simone':'simone','/node':'node','/moments':'moments','/community':'community','/graphic-design':'graphic-design'};
  var current = null;
  if('scrollRestoration' in history) history.scrollRestoration = 'manual';
  function route(first){
    var h = (location.hash || '').replace(/^#/, '');
    var view = 'home', tab = 'all';
    if(h.charAt(0) === '/'){ view = ROUTES[h] || 'home'; }
    else if(tabNames[h]){ tab = h; }
    var el = document.querySelector('.view[data-route="' + view + '"]');
    if(!el){ view = 'home'; el = document.querySelector('.view[data-route="home"]'); }
    var show = function(){
      document.querySelectorAll('.view').forEach(function(v){ v.hidden = v !== el; });
      document.title = el.dataset.title;
      var md = document.querySelector('meta[name="description"]'); if(md) md.setAttribute('content', el.dataset.desc);
      if(view === 'home') applyTab(tab);
      if(current !== view){ window.scrollTo(0, 0); hideTip(); }
      current = view;
    };
    if(first === true) show(); else morph(show);
  }
  window.addEventListener('hashchange', function(){ route(); });

  // The logo always returns to the very top of the main landing page (All tab), from anywhere.
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('a.logo'); if(!a) return;
    e.preventDefault();
    if(location.hash !== '#/') history.pushState(null, '', '#/');
    route();
    window.scrollTo({top: 0, behavior: reduce ? 'auto' : 'smooth'});
  });

  initPage();
  route(true);
})();
