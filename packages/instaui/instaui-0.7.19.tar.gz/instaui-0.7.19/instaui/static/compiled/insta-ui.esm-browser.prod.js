var Ir = Object.defineProperty;
var Dr = (e, t, n) => t in e ? Ir(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : e[t] = n;
var T = (e, t, n) => Dr(e, typeof t != "symbol" ? t + "" : t, n);
import * as Mr from "vue";
import { toRaw as _n, toValue as Se, normalizeClass as dt, normalizeStyle as En, cloneVNode as re, vModelDynamic as Br, vShow as jr, withDirectives as bn, h as q, toDisplayString as Sn, withModifiers as Lr, customRef as de, isRef as Vt, isVNode as Fr, resolveDynamicComponent as kn, normalizeProps as Rn, TransitionGroup as Ur, unref as Q, toRef as ge, readonly as Ct, ref as L, onBeforeUnmount as On, onMounted as At, nextTick as ke, getCurrentScope as Wr, onScopeDispose as zr, getCurrentInstance as Ge, watch as G, shallowRef as ce, watchEffect as xt, computed as B, inject as le, shallowReactive as Hr, defineComponent as X, reactive as Kr, provide as H, onUnmounted as Gr, useAttrs as Pn, createTextVNode as qr, onErrorCaptured as Jr, openBlock as ae, createElementBlock as ye, createElementVNode as Nn, createVNode as Qr, createCommentVNode as ht, mergeProps as he, createBlock as Vn, Teleport as Yr, renderSlot as pt, Fragment as Xr, useSlots as De, useTemplateRef as Zr, KeepAlive as es } from "vue";
let Cn;
function ts(e) {
  Cn = e;
}
function We() {
  return Cn;
}
function ze() {
  const { queryPath: e, pathParams: t, queryParams: n } = We();
  return {
    path: e,
    ...t === void 0 ? {} : { params: t },
    ...n === void 0 ? {} : { queryParams: n }
  };
}
function Ut(e, t) {
  Object.entries(e).forEach(([n, r]) => t(r, n));
}
function qe(e, t) {
  return An(e, {
    valueFn: t
  });
}
function An(e, t) {
  const { valueFn: n, keyFn: r } = t;
  return Object.fromEntries(
    Object.entries(e).map(([s, o], i) => [
      r ? r(s, o) : s,
      n(o, s, i)
    ])
  );
}
function ns(e, t, n) {
  if (Array.isArray(t)) {
    const [s, ...o] = t;
    switch (s) {
      case "!":
        return !e;
      case "+":
        return e + o[0];
      case "~+":
        return o[0] + e;
    }
  }
  const r = rs(t);
  return e[r];
}
function rs(e, t) {
  if (typeof e == "string" || typeof e == "number")
    return e;
  if (!Array.isArray(e))
    throw new Error(`Invalid path ${e}`);
  const [n, ...r] = e;
  switch (n) {
    case "bind":
      throw new Error("No bindable function provided");
    default:
      throw new Error(`Invalid flag ${n} in array at ${e}`);
  }
}
function ss(e, t, n) {
  return t.reduce(
    (r, s) => ns(r, s),
    e
  );
}
function os(e, t) {
  return t ? t.reduce((n, r) => n[r], e) : e;
}
const is = window.structuredClone || ((e) => JSON.parse(JSON.stringify(e)));
function $t(e) {
  if (typeof e == "function")
    return e;
  try {
    return is(_n(Se(e)));
  } catch {
    return e;
  }
}
function xn(e, t) {
  const n = e.classes;
  if (!n)
    return null;
  if (typeof n == "string")
    return dt(n);
  const { str: r, map: s, bind: o } = n, { bindingGetter: i } = t, a = [];
  return r && a.push(r), s && a.push(
    qe(
      s,
      (c) => i.getValue(c)
    )
  ), o && a.push(...o.map((c) => i.getValue(c))), dt(a);
}
function $n(e, t) {
  const n = [], { bindingGetter: r } = t, { dStyle: s = {}, sStyle: o = [] } = e;
  n.push(
    qe(
      s || {},
      (c) => r.getValue(c)
    )
  ), n.push(
    ...o.map((c) => r.getValue(c))
  );
  const i = En([e.style || {}, n]);
  return {
    hasStyle: i && Object.keys(i).length > 0,
    styles: i
  };
}
function Tn(e, t, n) {
  const r = [], { dir: s = [] } = t, { bindingGetter: o } = n;
  return s.forEach((i) => {
    const { sys: a, name: c, arg: d, value: u, mf: l } = i;
    if (c === "vmodel") {
      const f = o.getRef(u);
      if (e = re(e, {
        [`onUpdate:${d}`]: (h) => {
          f.value = h;
        }
      }), a === 1) {
        const h = l ? Object.fromEntries(l.map((p) => [p, !0])) : {};
        r.push([Br, f.value, void 0, h]);
      } else
        e = re(e, {
          [d]: f.value
        });
    } else if (c === "vshow") {
      const f = o.getValue(u);
      r.push([jr, f]);
    } else
      console.warn(`Directive ${c} is not supported yet`);
  }), r.length > 0 ? bn(e, r) : e;
}
function Me(e, t) {
  return q(Cr, {
    config: e,
    vforSetting: t == null ? void 0 : t.vforSetting,
    slotSetting: t == null ? void 0 : t.slotSetting
  });
}
function as(e, t, n) {
  if (!e.slots)
    return;
  const r = e.slots ?? {};
  if (t) {
    const o = r[":"];
    if (!o)
      return;
    const { scope: i, items: a } = o;
    return i ? Me(i, {
      buildOptions: n
    }) : a == null ? void 0 : a.map((c) => we(c, n));
  }
  return An(r, {
    keyFn: mt,
    valueFn: In(n)
  });
}
function In(e) {
  return (t) => {
    const { usePropId: n, scope: r } = t;
    return r ? (s) => Me(r, {
      buildOptions: e,
      slotSetting: n ? {
        id: n,
        value: s
      } : void 0
    }) : () => {
      var s;
      return (s = t.items) == null ? void 0 : s.map((o) => we(o, e));
    };
  };
}
function mt(e) {
  return e === ":" ? "default" : e;
}
function Y(e, t) {
  t = t || {};
  const n = [...Object.keys(t), "__Vue"], r = [...Object.values(t), Mr];
  try {
    return new Function(...n, `return (${e})`)(...r);
  } catch (s) {
    throw new Error(s + " in function code: " + e);
  }
}
function He(e, t = !0) {
  if (!(typeof e != "object" || e === null)) {
    if (Array.isArray(e)) {
      t && e.forEach((n) => He(n, !0));
      return;
    }
    for (const [n, r] of Object.entries(e))
      if (n.startsWith(":"))
        try {
          e[n.slice(1)] = new Function(`return (${r})`)(), delete e[n];
        } catch (s) {
          console.error(
            `Error while converting ${n} attribute to function:`,
            s
          );
        }
      else
        t && He(r, !0);
  }
}
function cs(e, t) {
  const n = e.startsWith(":");
  return n && (e = e.slice(1), t = Y(t)), { name: e, value: t, isFunc: n };
}
class ls {
  toString() {
    return "";
  }
}
const Te = new ls();
function Re(e) {
  return _n(e) === Te;
}
function Dn(e, t) {
  var o;
  const n = {}, r = e.props ?? {}, { bindingGetter: s } = t;
  return He(r), Ut(e.bProps || {}, (i, a) => {
    const c = s.getValue(i);
    Re(c) || (He(c), n[a] = us(c, a));
  }), (o = e.proxyProps) == null || o.forEach((i) => {
    const a = s.getValue(i);
    typeof a == "object" && Ut(a, (c, d) => {
      const { name: u, value: l } = cs(d, c);
      n[u] = l;
    });
  }), { ...r, ...n };
}
function us(e, t) {
  return t === "innerText" ? Sn(e) : e;
}
class fs {
  async eventSend(t, n) {
    const { fType: r, hKey: s, key: o } = t, i = We().webServerInfo, a = o !== void 0 ? { key: o } : {}, c = r === "sync" ? i.event_url : i.event_async_url;
    let d = {};
    const u = await fetch(c, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        bind: n,
        hKey: s,
        ...a,
        page: ze(),
        ...d
      })
    });
    if (!u.ok)
      throw new Error(`HTTP error! status: ${u.status}`);
    return await u.json();
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, s = We().webServerInfo, o = n === "sync" ? s.watch_url : s.watch_async_url, i = t.getServerInputs(), a = {
      key: r,
      input: i,
      page: ze()
    };
    return await (await fetch(o, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(a)
    })).json();
  }
}
class ds {
  async eventSend(t, n) {
    const { fType: r, hKey: s, key: o } = t, i = o !== void 0 ? { key: o } : {};
    let a = {};
    const c = {
      bind: n,
      fType: r,
      hKey: s,
      ...i,
      page: ze(),
      ...a
    };
    return await window.pywebview.api.event_call(c);
  }
  async watchSend(t) {
    const { fType: n, key: r } = t.watchConfig, s = t.getServerInputs(), o = {
      key: r,
      input: s,
      fType: n,
      page: ze()
    };
    return await window.pywebview.api.watch_call(o);
  }
}
let gt;
function hs(e) {
  switch (e) {
    case "web":
      gt = new fs();
      break;
    case "webview":
      gt = new ds();
      break;
  }
}
function Mn() {
  return gt;
}
function Bn(e) {
  const { config: t, bindingGetter: n } = e;
  if (!t)
    return {
      run: () => {
      },
      tryReset: () => {
      }
    };
  const r = t.map((i) => {
    const [a, c, d] = i, u = n.getRef(a);
    function l(f, h) {
      const { type: p, value: m } = h;
      if (p === "const") {
        f.value = m;
        return;
      }
      if (p === "action") {
        const y = ps(m, n);
        f.value = y;
        return;
      }
    }
    return {
      run: () => l(u, c),
      reset: () => l(u, d)
    };
  });
  return {
    run: () => {
      r.forEach((i) => i.run());
    },
    tryReset: () => {
      r.forEach((i) => i.reset());
    }
  };
}
function ps(e, t) {
  const { inputs: n = [], code: r } = e, s = Y(r), o = n.map((i) => t.getValue(i));
  return s(...o);
}
function Wt(e) {
  return e == null;
}
const se = {
  Ref: 0,
  EventContext: 1,
  Data: 2,
  JsFn: 3,
  ElementRef: 4,
  EventContextDataset: 5
}, zt = {
  const: "c",
  ref: "r",
  range: "n"
}, be = {
  Ref: 0,
  RouterAction: 1,
  ElementRefAction: 2,
  JsCode: 3,
  FileDownload: 4
};
class jn extends Error {
  constructor(t) {
    super(t), this.name = "BrowserNotSupportedError";
  }
}
function Ln(e, t) {
  switch (t) {
    case "kb":
      return e * 1024;
    case "mb":
      return e * 1024 * 1024;
    case "gb":
      return e * 1024 * 1024 * 1024;
    default:
      return e;
  }
}
class ms {
  constructor(t, n) {
    T(this, "filename");
    T(this, "filepath");
    T(this, "chuckedConfig");
    T(this, "onProgress");
    T(this, "onStatus");
    T(this, "controller", null);
    T(this, "receivedBytes", 0);
    T(this, "totalBytes", 0);
    T(this, "chunks", []);
    T(this, "downloading", !1);
    this.url = t, this.filename = n.filename, this.filepath = n.filepath, this.chuckedConfig = n.config, this.onProgress = () => {
    }, this.onStatus = () => {
    };
  }
  async start() {
    this.downloading || (this.downloading = !0, await this.fetchChunk(this.receivedBytes));
  }
  pause() {
    var t;
    this.downloading && (this.downloading = !1, (t = this.controller) == null || t.abort());
  }
  async resume() {
    this.downloading || (this.downloading = !0, await this.fetchChunk(this.receivedBytes));
  }
  async fetchChunk(t) {
    var d;
    this.controller = new AbortController();
    const n = Ln(
      this.chuckedConfig.chunk_size,
      this.chuckedConfig.chunk_size_unit
    ), r = new URLSearchParams({
      filepath: this.filepath,
      mode: "chunked",
      chunk_bytes: n.toString()
    }), s = `${this.url}?` + r.toString(), o = t ? { Range: `bytes=${t}-` } : {}, i = await fetch(s, {
      headers: o,
      signal: this.controller.signal
    });
    if (!i.ok && i.status !== 206 && i.status !== 200) {
      this.downloading = !1;
      return;
    }
    const a = i.headers.get("Content-Range");
    this.totalBytes = a && parseInt(a.split("/")[1]) || parseInt(i.headers.get("Content-Length") || "0", 10);
    const c = (d = i.body) == null ? void 0 : d.getReader();
    if (!c)
      throw new jn("Browser does not support streaming download");
    for (; this.downloading; ) {
      const { done: u, value: l } = await c.read();
      if (u) break;
      l && (this.chunks.push(l), this.receivedBytes += l.length, this.updateProgress());
    }
    this.receivedBytes >= this.totalBytes && this.finish();
  }
  updateProgress() {
    if (this.totalBytes > 0) {
      const t = parseFloat(
        (this.receivedBytes / this.totalBytes * 100).toFixed(2)
      );
      this.onProgress(t);
    } else
      (this.receivedBytes / 1024 / 1024).toFixed(2);
  }
  finish() {
    this.downloading = !1;
    const t = this.chunks.reduce(
      (i, a) => i + a.length,
      0
    ), n = new Uint8Array(t);
    let r = 0;
    for (const i of this.chunks)
      n.set(i, r), r += i.length;
    const s = new Blob([n]), o = document.createElement("a");
    o.href = URL.createObjectURL(s), o.download = this.filename, o.click(), URL.revokeObjectURL(o.href), this.chunks = [];
  }
  get progress() {
    return { received: this.receivedBytes, total: this.totalBytes };
  }
  get isDownloading() {
    return this.downloading;
  }
}
class yt {
  constructor(t, n) {
    T(this, "filename");
    T(this, "filepath");
    T(this, "onProgress");
    T(this, "onStatus");
    T(this, "controller", null);
    T(this, "receivedBytes", 0);
    T(this, "totalBytes", 0);
    T(this, "downloading", !1);
    this.url = t, this.filename = n.filename, this.filepath = n.filepath, this.onProgress = () => {
    }, this.onStatus = () => {
    };
  }
  async start() {
    this.downloading || (this.downloading = !0, await this.downloadFile());
  }
  pause() {
    var t;
    this.downloading && (this.downloading = !1, (t = this.controller) == null || t.abort());
  }
  async downloadFile() {
    var r;
    this.controller = new AbortController();
    const t = new URLSearchParams({ filepath: this.filepath }), n = `${this.url}?` + t.toString();
    try {
      const s = await fetch(n, {
        signal: this.controller.signal
      });
      if (!s.ok) {
        this.onStatus(`Download failed: ${s.statusText}`), this.downloading = !1;
        return;
      }
      this.totalBytes = parseInt(s.headers.get("Content-Length") || "0", 10);
      const o = (r = s.body) == null ? void 0 : r.getReader();
      if (!o) {
        this.onStatus("Web Browser not support download file"), this.downloading = !1;
        return;
      }
      const i = [];
      for (; this.downloading; ) {
        const { done: a, value: c } = await o.read();
        if (a) break;
        c && (i.push(c), this.receivedBytes += c.length, this.updateProgress());
      }
      this.receivedBytes >= this.totalBytes && this.finishDownload(i);
    } catch (s) {
      this.onStatus(`Download error: ${s instanceof Error ? s.message : String(s)}`), this.downloading = !1;
    }
  }
  updateProgress() {
    if (this.totalBytes > 0) {
      const t = parseFloat(
        (this.receivedBytes / this.totalBytes * 100).toFixed(2)
      );
      this.onProgress(t);
    }
  }
  finishDownload(t) {
    this.downloading = !1;
    const n = t.reduce((a, c) => a + c.length, 0), r = new Uint8Array(n);
    let s = 0;
    for (const a of t)
      r.set(a, s), s += a.length;
    const o = new Blob([r]), i = document.createElement("a");
    i.href = URL.createObjectURL(o), i.download = this.filename, i.click(), URL.revokeObjectURL(i.href);
  }
  get progress() {
    return { received: this.receivedBytes, total: this.totalBytes };
  }
  get isDownloading() {
    return this.downloading;
  }
}
async function gs(e) {
  const t = We().webServerInfo.download_url;
  if (e.mode === "auto") {
    if (!e.config)
      throw new Error("Auto mode requires config parameters");
    const n = e.config, r = Ln(
      n.threshold_size,
      n.threshold_size_unit
    );
    e.filesize < r ? await new yt(t, e).start() : await Ht(t, e);
    return;
  }
  if (e.mode === "chunked") {
    await Ht(t, e);
    return;
  }
  if (e.mode === "standard") {
    await new yt(t, e).start();
    return;
  }
}
async function Ht(e, t) {
  try {
    await new ms(e, t).start();
  } catch (n) {
    if (n instanceof jn)
      await new yt(e, t).start();
    else
      throw n;
  }
}
function Je(e, t, n) {
  if (Wt(t) || Wt(e.values))
    return;
  t = t;
  const r = e.values, s = e.types ?? Array.from({ length: t.length }).fill(0);
  t.forEach((o, i) => {
    const a = s[i];
    if (a === 1)
      return;
    if (o.type === be.Ref) {
      if (a === 2) {
        r[i].forEach(([u, l]) => {
          const f = o.ref, h = {
            ...f,
            path: [...f.path ?? [], ...u]
          };
          n.updateValue(h, l);
        });
        return;
      }
      n.updateValue(o.ref, r[i]);
      return;
    }
    if (o.type === be.RouterAction) {
      const d = r[i], u = n.getRouter(o.ref)[d.fn];
      u(...d.args);
      return;
    }
    if (o.type === be.ElementRefAction) {
      const d = o.ref, u = n.getRef(d).value, l = r[i], { method: f, args: h = [] } = l;
      u[f](...h);
      return;
    }
    if (o.type === be.JsCode) {
      const d = r[i];
      if (!d)
        return;
      const u = Y(d);
      Promise.resolve(u());
      return;
    }
    if (o.type === be.FileDownload) {
      const d = r[i];
      gs(d);
      return;
    }
    const c = n.getRef(o.ref);
    c.value = r[i];
  });
}
class ys extends Map {
  constructor(t) {
    super(), this.factory = t;
  }
  getOrDefault(t) {
    if (!this.has(t)) {
      const n = this.factory();
      return this.set(t, n), n;
    }
    return super.get(t);
  }
}
function Fn(e) {
  return new ys(e);
}
const vs = "on:mounted";
function Un(e, t, n) {
  if (!t)
    return e;
  const r = Fn(() => []);
  t.map(([a, c]) => {
    const d = ws(c, n), { eventName: u, handleEvent: l } = ks({
      eventName: a,
      info: c,
      handleEvent: d
    });
    r.getOrDefault(u).push(l);
  });
  const s = {};
  for (const [a, c] of r) {
    const d = c.length === 1 ? c[0] : (...u) => c.forEach((l) => Promise.resolve().then(() => l(...u)));
    s[a] = d;
  }
  const { [vs]: o, ...i } = s;
  return e = re(e, i), o && (e = bn(e, [
    [
      {
        mounted(a) {
          o(a);
        }
      }
    ]
  ])), e;
}
function ws(e, t) {
  if (e.type === "web") {
    const n = _s(e, t);
    return Es(e, n, t);
  } else {
    if (e.type === "vue")
      return Ss(e, t);
    if (e.type === "js")
      return bs(e, t);
  }
  throw new Error(`unknown event type ${e}`);
}
function _s(e, t) {
  const { inputs: n = [] } = e, { bindingGetter: r } = t;
  return (...s) => n.map(({ value: o, type: i }) => {
    if (i === se.EventContext || i === se.EventContextDataset) {
      const { path: a } = o;
      if (a.startsWith(":")) {
        const c = a.slice(1);
        return Y(c)(...s);
      }
      return os(s[0], a.split("."));
    }
    return i === se.Ref ? r.getValue(o) : o;
  });
}
function Es(e, t, n) {
  const { bindingGetter: r } = n;
  async function s(...o) {
    const i = t(...o), a = Bn({
      config: e.preSetup,
      bindingGetter: r
    });
    try {
      a.run();
      const c = await Mn().eventSend(e, i);
      if (!c)
        return;
      Je(c, e.sets, r);
    } finally {
      a.tryReset();
    }
  }
  return s;
}
function bs(e, t) {
  const { sets: n, code: r, inputs: s = [] } = e, { bindingGetter: o } = t, i = Y(r);
  async function a(...c) {
    const d = s.map(({ value: l, type: f }) => {
      const h = f === se.EventContextDataset;
      if (f === se.EventContext || h) {
        if (l.path.startsWith(":")) {
          const p = l.path.slice(1), m = Y(p)(...c);
          return m == null ? m : h ? JSON.parse(m) : m;
        }
        return ss(c[0], l.path.split("."));
      }
      if (f === se.Ref)
        return o.getValue(l);
      if (f === se.Data)
        return l;
      if (f === se.ElementRef || f === se.JsFn)
        return o.getValue(l);
      throw new Error(`unknown input type ${f}`);
    }), u = await i(...d);
    if (n !== void 0) {
      const f = n.length === 1 ? [u] : u, h = f.map((p) => p === void 0 ? 1 : 0);
      Je(
        { values: f, types: h },
        n,
        o
      );
    }
  }
  return a;
}
function Ss(e, t) {
  const { code: n, inputs: r = {} } = e, { bindingGetter: s } = t, o = qe(
    r,
    (c) => c.type !== se.Data ? s.getRef(c.value) : c.value
  ), i = Y(n, o);
  function a(...c) {
    i(...c);
  }
  return a;
}
function ks(e) {
  const { eventName: t, info: n, handleEvent: r } = e;
  if (n.type === "vue")
    return {
      eventName: t,
      handleEvent: r
    };
  const { modifier: s = [] } = n;
  if (s.length === 0)
    return {
      eventName: t,
      handleEvent: r
    };
  const o = ["passive", "capture", "once"], i = [], a = [];
  for (const u of s)
    o.includes(u) ? i.push(u[0].toUpperCase() + u.slice(1)) : a.push(u);
  const c = i.length > 0 ? t + i.join("") : t, d = a.length > 0 ? Lr(r, a) : r;
  return {
    eventName: c,
    handleEvent: d
  };
}
function Wn(e, t, n) {
  const { eRef: r } = t, { bindingGetter: s } = n;
  return r ? re(e, { ref: s.getRef(r) }) : e;
}
function zn(e, t, n) {
  const [r] = t;
  switch (r) {
    case "bind":
      return e[K(t, n)];
    case "!":
      return !e;
    case "+":
      return e + K(t, n);
    case "~+":
      return K(t, n) + e;
    case "-":
      return e - K(t, n);
    case "~-":
      return K(t, n) - e;
    case "*":
      return e * K(t, n);
    case "~*":
      return K(t, n) * e;
    case "/":
      return e / K(t, n);
    case "~/":
      return K(t, n) / e;
    case "<":
      return e < K(t, n);
    case "<=":
      return e <= K(t, n);
    case ">":
      return e > K(t, n);
    case ">=":
      return e >= K(t, n);
    case "==":
      return e == K(t, n);
    case "!=":
      return e != K(t, n);
    case "||":
      return e || K(t, n);
    case "&&":
      return e && K(t, n);
    case "len":
      return e.length;
    default:
      throw new Error(`Invalid flag ${r} in array at ${t}`);
  }
}
function K(e, t) {
  const [n, r, s] = e, o = () => s && s[0] ? t(r[0]) : r[0];
  switch (n) {
    case "bind":
    case "+":
    case "~+":
    case "-":
    case "~-":
    case "*":
    case "~*":
    case "/":
    case "~/":
    case "<":
    case "<=":
    case ">":
    case ">=":
    case "==":
    case "!=":
    case "||":
    case "&&":
      return o();
    default:
      throw new Error(`Invalid flag ${n} in array at ${e}`);
  }
}
function Rs(e, t, n) {
  return Kn(t).reduce(
    (r, s) => zn(r, s, n),
    e
  );
}
function Hn(e, t, n, r) {
  Kn(t).reduce((s, o, i) => {
    if (i === t.length - 1)
      s[K(o, r)] = n;
    else
      return zn(s, o, r);
  }, e);
}
function Kn(e) {
  return Os(e) ? e.map((t) => ["bind", [t]]) : e;
}
function Os(e) {
  return !Array.isArray(e[0]);
}
function Ps(e, t, n) {
  const { paths: r, getBindableValueFn: s } = t, { paths: o, getBindableValueFn: i } = t;
  return r === void 0 || r.length === 0 ? e : de(() => ({
    get() {
      try {
        return Rs(
          Se(e),
          r,
          s
        );
      } catch {
        return;
      }
    },
    set(a) {
      Hn(
        Se(e),
        o || r,
        a,
        i
      );
    }
  }));
}
function Kt(e, t) {
  return !Re(e) && JSON.stringify(t) === JSON.stringify(e);
}
function Tt(e) {
  if (Vt(e)) {
    const t = e;
    return de(() => ({
      get() {
        return Se(t);
      },
      set(n) {
        const r = Se(t);
        Kt(r, n) || (t.value = n);
      }
    }));
  }
  return de((t, n) => ({
    get() {
      return t(), e;
    },
    set(r) {
      Kt(e, r) || (e = r, n());
    }
  }));
}
function Gn(e) {
  return Fr(e) || e instanceof Element;
}
function Ns(e, t) {
  const n = e.setup;
  return {
    ...e,
    setup(r, s) {
      return t(), n ? n(r, s) : void 0;
    }
  };
}
function vt(e, t, n, r) {
  const s = Vs(e, t), o = kn(s), i = typeof o == "string", a = xn(e, t), { styles: c, hasStyle: d } = $n(e, t), u = as(e, i, t), l = Dn(e, t), f = Rn(l) || {};
  d && (f.style = c), a && (f.class = a);
  const h = n ? Ns(o, n) : o;
  let p = q(h, { ...f, ...r }, u);
  return p = Un(p, e.events, t), p = Wn(p, e, t), Tn(p, e, t);
}
function Vs(e, t) {
  const { tag: n } = e;
  return typeof n == "string" ? n : t.bindingGetter.getValue(n);
}
function Cs(e, t) {
  var l, f, h;
  const { fkey: n, tsGroup: r = {}, scope: s } = e, o = !!((l = e.used) != null && l.item), i = !!((f = e.used) != null && f.index), a = !!((h = e.used) != null && h.key), c = [], { sourceInfo: d, iterSource: u } = qn(e, t);
  for (const [p, m, y] of u) {
    const w = As(
      o,
      m,
      e,
      d,
      p,
      y,
      i,
      a
    );
    let _ = Me(s, {
      buildOptions: t,
      vforSetting: w
    });
    const k = Jn(n, { value: m, index: p });
    _ = re(_, { key: k }), c.push(_);
  }
  return r && Object.keys(r).length > 0 ? q(Ur, r, {
    default: () => c
  }) : c;
}
function As(e, t, n, r, s, o, i, a) {
  const c = {};
  return e && (c.item = {
    value: t,
    id: n.used.item
  }, r && (c.item.sourceInfo = {
    source: r.source,
    type: r.type,
    index: s,
    key: o
  })), i && (c.index = {
    value: s,
    id: n.used.index
  }), a && (c.key = {
    value: o,
    id: n.used.key
  }), c;
}
function qn(e, t) {
  const { type: n, value: r } = e.array, { bindingGetter: s } = t, o = n === zt.range, i = n === zt.const || o && typeof r == "number";
  if (o) {
    const { start: a = 0, end: c, step: d = 1 } = r, u = typeof a == "number" ? a : s.getValue(a), l = typeof c == "number" ? c : s.getValue(c), f = typeof d == "number" ? d : s.getValue(d);
    return {
      sourceInfo: void 0,
      iterSource: Gt(u, l, f)
    };
  }
  {
    const a = i ? r : s.getValue(e.array.value);
    if (typeof a == "number")
      return {
        sourceInfo: void 0,
        iterSource: Gt(0, a, 1)
      };
    if (Array.isArray(a)) {
      function* c() {
        for (let d = 0; d < a.length; d++)
          yield [d, a[d]];
      }
      return {
        sourceInfo: i ? void 0 : {
          source: s.getRef(e.array.value),
          type: "array"
        },
        iterSource: c()
      };
    }
    if (typeof a == "object" && a !== null) {
      function* c() {
        let d = 0;
        for (const [u, l] of Object.entries(a))
          yield [d++, l, u];
      }
      return {
        sourceInfo: i ? void 0 : {
          source: s.getRef(e.array.value),
          type: "object"
        },
        iterSource: c()
      };
    }
    if (Re(a))
      return a;
  }
  throw new Error("Not implemented yet");
}
function* Gt(e, t, n = 1) {
  if (n === 0)
    throw new Error("Step cannot be 0");
  let r = 0;
  if (n > 0)
    for (let s = e; s < t; s += n)
      yield [r++, s];
  else
    for (let s = e; s > t; s += n)
      yield [r++, s];
}
const xs = (e) => e, $s = (e, t) => t;
function Jn(e, t) {
  const { value: n, index: r } = t, s = Ts(e ?? "index");
  return typeof s == "function" ? s(n, r) : e === "item" ? xs(n) : $s(n, r);
}
function Ts(e) {
  const t = e.trim();
  if (t === "item" || t === "index")
    return;
  if (e.startsWith(":")) {
    e = e.slice(1);
    try {
      return Y(e);
    } catch (r) {
      throw new Error(r + " in function code: " + e);
    }
  }
  const n = `(item, index) => { return ${t}; }`;
  try {
    return Y(n);
  } catch (r) {
    throw new Error(r + " in function code: " + n);
  }
}
function Qn(e) {
  return "r" in e;
}
function It(e) {
  return Wr() ? (zr(e), !0) : !1;
}
function ne(e) {
  return typeof e == "function" ? e() : Q(e);
}
const Yn = typeof window < "u" && typeof document < "u";
typeof WorkerGlobalScope < "u" && globalThis instanceof WorkerGlobalScope;
const Is = (e) => e != null, Ds = Object.prototype.toString, Ms = (e) => Ds.call(e) === "[object Object]", Ie = () => {
};
function Bs(e, t) {
  function n(...r) {
    return new Promise((s, o) => {
      Promise.resolve(e(() => t.apply(this, r), { fn: t, thisArg: this, args: r })).then(s).catch(o);
    });
  }
  return n;
}
const Xn = (e) => e();
function js(e = Xn) {
  const t = L(!0);
  function n() {
    t.value = !1;
  }
  function r() {
    t.value = !0;
  }
  const s = (...o) => {
    t.value && e(...o);
  };
  return { isActive: Ct(t), pause: n, resume: r, eventFilter: s };
}
function wt(e, t = !1, n = "Timeout") {
  return new Promise((r, s) => {
    setTimeout(t ? () => s(n) : r, e);
  });
}
function Zn(e) {
  return Ge();
}
function er(...e) {
  if (e.length !== 1)
    return ge(...e);
  const t = e[0];
  return typeof t == "function" ? Ct(de(() => ({ get: t, set: Ie }))) : L(t);
}
function Ls(e, t, n = {}) {
  const {
    eventFilter: r = Xn,
    ...s
  } = n;
  return G(
    e,
    Bs(
      r,
      t
    ),
    s
  );
}
function Fs(e, t, n = {}) {
  const {
    eventFilter: r,
    ...s
  } = n, { eventFilter: o, pause: i, resume: a, isActive: c } = js(r);
  return { stop: Ls(
    e,
    t,
    {
      ...s,
      eventFilter: o
    }
  ), pause: i, resume: a, isActive: c };
}
function Us(e, t) {
  Zn() && On(e, t);
}
function tr(e, t = !0, n) {
  Zn() ? At(e, n) : t ? e() : ke(e);
}
function _t(e, t = !1) {
  function n(l, { flush: f = "sync", deep: h = !1, timeout: p, throwOnTimeout: m } = {}) {
    let y = null;
    const _ = [new Promise((k) => {
      y = G(
        e,
        (v) => {
          l(v) !== t && (y ? y() : ke(() => y == null ? void 0 : y()), k(v));
        },
        {
          flush: f,
          deep: h,
          immediate: !0
        }
      );
    })];
    return p != null && _.push(
      wt(p, m).then(() => ne(e)).finally(() => y == null ? void 0 : y())
    ), Promise.race(_);
  }
  function r(l, f) {
    if (!Vt(l))
      return n((v) => v === l, f);
    const { flush: h = "sync", deep: p = !1, timeout: m, throwOnTimeout: y } = f ?? {};
    let w = null;
    const k = [new Promise((v) => {
      w = G(
        [e, l],
        ([R, A]) => {
          t !== (R === A) && (w ? w() : ke(() => w == null ? void 0 : w()), v(R));
        },
        {
          flush: h,
          deep: p,
          immediate: !0
        }
      );
    })];
    return m != null && k.push(
      wt(m, y).then(() => ne(e)).finally(() => (w == null || w(), ne(e)))
    ), Promise.race(k);
  }
  function s(l) {
    return n((f) => !!f, l);
  }
  function o(l) {
    return r(null, l);
  }
  function i(l) {
    return r(void 0, l);
  }
  function a(l) {
    return n(Number.isNaN, l);
  }
  function c(l, f) {
    return n((h) => {
      const p = Array.from(h);
      return p.includes(l) || p.includes(ne(l));
    }, f);
  }
  function d(l) {
    return u(1, l);
  }
  function u(l = 1, f) {
    let h = -1;
    return n(() => (h += 1, h >= l), f);
  }
  return Array.isArray(ne(e)) ? {
    toMatch: n,
    toContains: c,
    changed: d,
    changedTimes: u,
    get not() {
      return _t(e, !t);
    }
  } : {
    toMatch: n,
    toBe: r,
    toBeTruthy: s,
    toBeNull: o,
    toBeNaN: a,
    toBeUndefined: i,
    changed: d,
    changedTimes: u,
    get not() {
      return _t(e, !t);
    }
  };
}
function Ws(e) {
  return _t(e);
}
function zs(e, t, n) {
  let r;
  Vt(n) ? r = {
    evaluating: n
  } : r = n || {};
  const {
    lazy: s = !1,
    evaluating: o = void 0,
    shallow: i = !0,
    onError: a = Ie
  } = r, c = L(!s), d = i ? ce(t) : L(t);
  let u = 0;
  return xt(async (l) => {
    if (!c.value)
      return;
    u++;
    const f = u;
    let h = !1;
    o && Promise.resolve().then(() => {
      o.value = !0;
    });
    try {
      const p = await e((m) => {
        l(() => {
          o && (o.value = !1), h || m();
        });
      });
      f === u && (d.value = p);
    } catch (p) {
      a(p);
    } finally {
      o && f === u && (o.value = !1), h = !0;
    }
  }), s ? B(() => (c.value = !0, d.value)) : d;
}
const Oe = Yn ? window : void 0, Hs = Yn ? window.document : void 0;
function Dt(e) {
  var t;
  const n = ne(e);
  return (t = n == null ? void 0 : n.$el) != null ? t : n;
}
function qt(...e) {
  let t, n, r, s;
  if (typeof e[0] == "string" || Array.isArray(e[0]) ? ([n, r, s] = e, t = Oe) : [t, n, r, s] = e, !t)
    return Ie;
  Array.isArray(n) || (n = [n]), Array.isArray(r) || (r = [r]);
  const o = [], i = () => {
    o.forEach((u) => u()), o.length = 0;
  }, a = (u, l, f, h) => (u.addEventListener(l, f, h), () => u.removeEventListener(l, f, h)), c = G(
    () => [Dt(t), ne(s)],
    ([u, l]) => {
      if (i(), !u)
        return;
      const f = Ms(l) ? { ...l } : l;
      o.push(
        ...n.flatMap((h) => r.map((p) => a(u, h, p, f)))
      );
    },
    { immediate: !0, flush: "post" }
  ), d = () => {
    c(), i();
  };
  return It(d), d;
}
function Ks() {
  const e = L(!1), t = Ge();
  return t && At(() => {
    e.value = !0;
  }, t), e;
}
function nr(e) {
  const t = Ks();
  return B(() => (t.value, !!e()));
}
function Gs(e, t, n = {}) {
  const { window: r = Oe, ...s } = n;
  let o;
  const i = nr(() => r && "MutationObserver" in r), a = () => {
    o && (o.disconnect(), o = void 0);
  }, c = B(() => {
    const f = ne(e), h = (Array.isArray(f) ? f : [f]).map(Dt).filter(Is);
    return new Set(h);
  }), d = G(
    () => c.value,
    (f) => {
      a(), i.value && f.size && (o = new MutationObserver(t), f.forEach((h) => o.observe(h, s)));
    },
    { immediate: !0, flush: "post" }
  ), u = () => o == null ? void 0 : o.takeRecords(), l = () => {
    d(), a();
  };
  return It(l), {
    isSupported: i,
    stop: l,
    takeRecords: u
  };
}
function qs(e, t, n) {
  const {
    immediate: r = !0,
    delay: s = 0,
    onError: o = Ie,
    onSuccess: i = Ie,
    resetOnExecute: a = !0,
    shallow: c = !0,
    throwError: d
  } = {}, u = c ? ce(t) : L(t), l = L(!1), f = L(!1), h = ce(void 0);
  async function p(w = 0, ..._) {
    a && (u.value = t), h.value = void 0, l.value = !1, f.value = !0, w > 0 && await wt(w);
    const k = typeof e == "function" ? e(..._) : e;
    try {
      const v = await k;
      u.value = v, l.value = !0, i(v);
    } catch (v) {
      if (h.value = v, o(v), d)
        throw v;
    } finally {
      f.value = !1;
    }
    return u.value;
  }
  r && p(s);
  const m = {
    state: u,
    isReady: l,
    isLoading: f,
    error: h,
    execute: p
  };
  function y() {
    return new Promise((w, _) => {
      Ws(f).toBe(!1).then(() => w(m)).catch(_);
    });
  }
  return {
    ...m,
    then(w, _) {
      return y().then(w, _);
    }
  };
}
function Js(e, t = {}) {
  const { window: n = Oe } = t, r = nr(() => n && "matchMedia" in n && typeof n.matchMedia == "function");
  let s;
  const o = L(!1), i = (d) => {
    o.value = d.matches;
  }, a = () => {
    s && ("removeEventListener" in s ? s.removeEventListener("change", i) : s.removeListener(i));
  }, c = xt(() => {
    r.value && (a(), s = n.matchMedia(ne(e)), "addEventListener" in s ? s.addEventListener("change", i) : s.addListener(i), o.value = s.matches);
  });
  return It(() => {
    c(), a(), s = void 0;
  }), o;
}
const Le = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {}, Fe = "__vueuse_ssr_handlers__", Qs = /* @__PURE__ */ Ys();
function Ys() {
  return Fe in Le || (Le[Fe] = Le[Fe] || {}), Le[Fe];
}
function rr(e, t) {
  return Qs[e] || t;
}
function Xs(e) {
  return Js("(prefers-color-scheme: dark)", e);
}
function Zs(e) {
  return e == null ? "any" : e instanceof Set ? "set" : e instanceof Map ? "map" : e instanceof Date ? "date" : typeof e == "boolean" ? "boolean" : typeof e == "string" ? "string" : typeof e == "object" ? "object" : Number.isNaN(e) ? "any" : "number";
}
const eo = {
  boolean: {
    read: (e) => e === "true",
    write: (e) => String(e)
  },
  object: {
    read: (e) => JSON.parse(e),
    write: (e) => JSON.stringify(e)
  },
  number: {
    read: (e) => Number.parseFloat(e),
    write: (e) => String(e)
  },
  any: {
    read: (e) => e,
    write: (e) => String(e)
  },
  string: {
    read: (e) => e,
    write: (e) => String(e)
  },
  map: {
    read: (e) => new Map(JSON.parse(e)),
    write: (e) => JSON.stringify(Array.from(e.entries()))
  },
  set: {
    read: (e) => new Set(JSON.parse(e)),
    write: (e) => JSON.stringify(Array.from(e))
  },
  date: {
    read: (e) => new Date(e),
    write: (e) => e.toISOString()
  }
}, Jt = "vueuse-storage";
function Et(e, t, n, r = {}) {
  var s;
  const {
    flush: o = "pre",
    deep: i = !0,
    listenToStorageChanges: a = !0,
    writeDefaults: c = !0,
    mergeDefaults: d = !1,
    shallow: u,
    window: l = Oe,
    eventFilter: f,
    onError: h = (N) => {
      console.error(N);
    },
    initOnMounted: p
  } = r, m = (u ? ce : L)(typeof t == "function" ? t() : t);
  if (!n)
    try {
      n = rr("getDefaultStorage", () => {
        var N;
        return (N = Oe) == null ? void 0 : N.localStorage;
      })();
    } catch (N) {
      h(N);
    }
  if (!n)
    return m;
  const y = ne(t), w = Zs(y), _ = (s = r.serializer) != null ? s : eo[w], { pause: k, resume: v } = Fs(
    m,
    () => A(m.value),
    { flush: o, deep: i, eventFilter: f }
  );
  l && a && tr(() => {
    n instanceof Storage ? qt(l, "storage", U) : qt(l, Jt, Z), p && U();
  }), p || U();
  function R(N, M) {
    if (l) {
      const W = {
        key: e,
        oldValue: N,
        newValue: M,
        storageArea: n
      };
      l.dispatchEvent(n instanceof Storage ? new StorageEvent("storage", W) : new CustomEvent(Jt, {
        detail: W
      }));
    }
  }
  function A(N) {
    try {
      const M = n.getItem(e);
      if (N == null)
        R(M, null), n.removeItem(e);
      else {
        const W = _.write(N);
        M !== W && (n.setItem(e, W), R(M, W));
      }
    } catch (M) {
      h(M);
    }
  }
  function I(N) {
    const M = N ? N.newValue : n.getItem(e);
    if (M == null)
      return c && y != null && n.setItem(e, _.write(y)), y;
    if (!N && d) {
      const W = _.read(M);
      return typeof d == "function" ? d(W, y) : w === "object" && !Array.isArray(W) ? { ...y, ...W } : W;
    } else return typeof M != "string" ? M : _.read(M);
  }
  function U(N) {
    if (!(N && N.storageArea !== n)) {
      if (N && N.key == null) {
        m.value = y;
        return;
      }
      if (!(N && N.key !== e)) {
        k();
        try {
          (N == null ? void 0 : N.newValue) !== _.write(m.value) && (m.value = I(N));
        } catch (M) {
          h(M);
        } finally {
          N ? ke(v) : v();
        }
      }
    }
  }
  function Z(N) {
    U(N.detail);
  }
  return m;
}
const to = "*,*::before,*::after{-webkit-transition:none!important;-moz-transition:none!important;-o-transition:none!important;-ms-transition:none!important;transition:none!important}";
function no(e = {}) {
  const {
    selector: t = "html",
    attribute: n = "class",
    initialValue: r = "auto",
    window: s = Oe,
    storage: o,
    storageKey: i = "vueuse-color-scheme",
    listenToStorageChanges: a = !0,
    storageRef: c,
    emitAuto: d,
    disableTransition: u = !0
  } = e, l = {
    auto: "",
    light: "light",
    dark: "dark",
    ...e.modes || {}
  }, f = Xs({ window: s }), h = B(() => f.value ? "dark" : "light"), p = c || (i == null ? er(r) : Et(i, r, o, { window: s, listenToStorageChanges: a })), m = B(() => p.value === "auto" ? h.value : p.value), y = rr(
    "updateHTMLAttrs",
    (v, R, A) => {
      const I = typeof v == "string" ? s == null ? void 0 : s.document.querySelector(v) : Dt(v);
      if (!I)
        return;
      const U = /* @__PURE__ */ new Set(), Z = /* @__PURE__ */ new Set();
      let N = null;
      if (R === "class") {
        const W = A.split(/\s/g);
        Object.values(l).flatMap((te) => (te || "").split(/\s/g)).filter(Boolean).forEach((te) => {
          W.includes(te) ? U.add(te) : Z.add(te);
        });
      } else
        N = { key: R, value: A };
      if (U.size === 0 && Z.size === 0 && N === null)
        return;
      let M;
      u && (M = s.document.createElement("style"), M.appendChild(document.createTextNode(to)), s.document.head.appendChild(M));
      for (const W of U)
        I.classList.add(W);
      for (const W of Z)
        I.classList.remove(W);
      N && I.setAttribute(N.key, N.value), u && (s.getComputedStyle(M).opacity, document.head.removeChild(M));
    }
  );
  function w(v) {
    var R;
    y(t, n, (R = l[v]) != null ? R : v);
  }
  function _(v) {
    e.onChanged ? e.onChanged(v, w) : w(v);
  }
  G(m, _, { flush: "post", immediate: !0 }), tr(() => _(m.value));
  const k = B({
    get() {
      return d ? p.value : m.value;
    },
    set(v) {
      p.value = v;
    }
  });
  return Object.assign(k, { store: p, system: h, state: m });
}
function ro(e = {}) {
  const {
    valueDark: t = "dark",
    valueLight: n = ""
  } = e, r = no({
    ...e,
    onChanged: (i, a) => {
      var c;
      e.onChanged ? (c = e.onChanged) == null || c.call(e, i === "dark", a, i) : a(i);
    },
    modes: {
      dark: t,
      light: n
    }
  }), s = B(() => r.system.value);
  return B({
    get() {
      return r.value === "dark";
    },
    set(i) {
      const a = i ? "dark" : "light";
      s.value === a ? r.value = "auto" : r.value = a;
    }
  });
}
function so(e = null, t = {}) {
  var n, r, s;
  const {
    document: o = Hs,
    restoreOnUnmount: i = (l) => l
  } = t, a = (n = o == null ? void 0 : o.title) != null ? n : "", c = er((r = e ?? (o == null ? void 0 : o.title)) != null ? r : null), d = e && typeof e == "function";
  function u(l) {
    if (!("titleTemplate" in t))
      return l;
    const f = t.titleTemplate || "%s";
    return typeof f == "function" ? f(l) : ne(f).replace(/%s/g, l);
  }
  return G(
    c,
    (l, f) => {
      l !== f && o && (o.title = u(typeof l == "string" ? l : ""));
    },
    { immediate: !0 }
  ), t.observe && !t.titleTemplate && o && !d && Gs(
    (s = o.head) == null ? void 0 : s.querySelector("title"),
    () => {
      o && o.title !== c.value && (c.value = u(o.title));
    },
    { childList: !0 }
  ), Us(() => {
    if (i) {
      const l = i(a, c.value || "");
      l != null && o && (o.title = l);
    }
  }), c;
}
function sr(e) {
  return e.constructor.name === "AsyncFunction";
}
function oo(e, t, n) {
  const r = /* @__PURE__ */ new Map(), s = /* @__PURE__ */ new Map(), o = /* @__PURE__ */ new Map();
  for (const c of e) {
    const d = n(c);
    r.set(d, 0), s.set(d, []), o.set(d, c);
  }
  for (const [c, d] of t)
    s.has(c) || s.set(c, []), s.get(c).push(d), r.set(d, (r.get(d) ?? 0) + 1);
  const i = [];
  for (const [c, d] of r.entries())
    d === 0 && i.push(c);
  const a = [];
  for (; i.length; ) {
    const c = i.shift(), d = o.get(c);
    if (d) {
      a.push(d);
      for (const u of s.get(c) ?? [])
        r.set(u, r.get(u) - 1), r.get(u) === 0 && i.push(u);
    }
  }
  if (a.length !== e.length)
    throw new Error(
      "Graph has at least one cycle; topological sort not possible."
    );
  return a;
}
function io(e) {
  const { type: t, key: n, value: r } = e.args;
  return t === "local" ? Et(n, r) : Et(n, r, sessionStorage);
}
const ao = "insta-color-scheme";
function co(e) {
  return ro({
    storageKey: ao,
    onChanged(n) {
      n ? (document.documentElement.setAttribute("theme-mode", "dark"), document.documentElement.classList.add("insta-dark")) : (document.documentElement.setAttribute("theme-mode", "light"), document.documentElement.classList.remove("insta-dark"));
    }
  });
}
function lo(e) {
  return so();
}
const uo = L("en_US");
function fo() {
  return uo;
}
const ho = /* @__PURE__ */ new Map([
  ["storage", io],
  ["useDark", co],
  ["usePageTitle", lo],
  ["useLanguage", fo]
]);
function po(e) {
  const { type: t } = e;
  if (!t)
    throw new Error("Invalid ref type");
  const n = ho.get(t);
  if (!n)
    throw new Error(`Invalid ref type ${t}`);
  return n(e);
}
function mo(e) {
  if (!e) return null;
  switch (e) {
    case "unwrap_reactive":
      return go;
    default:
      throw new Error(`Invalid js computed tool ${e}`);
  }
}
function go(e, t, ...n) {
  const r = $t(e);
  return t.forEach((s, o) => {
    const i = n[o];
    let a = r;
    for (let d = 0; d < s.length - 1; d++) {
      const u = s[d];
      a = a[u];
    }
    const c = s[s.length - 1];
    a[c] = i;
  }), r;
}
function yo(e, t) {
  const { deepCompare: n = !1, type: r } = e;
  if (!r) {
    const { value: s } = e;
    return n ? Tt(s) : L(s);
  }
  return po(e);
}
function vo(e, t, n) {
  const { bind: r = {}, code: s, const: o = [] } = e, i = Object.values(r).map((u, l) => o[l] === 1 ? u : t.getRef(u));
  if (sr(new Function(s)))
    return zs(
      async () => {
        const u = Object.fromEntries(
          Object.keys(r).map((l, f) => [l, i[f]])
        );
        return await Y(s, u)();
      },
      null,
      { lazy: !0 }
    );
  const a = Object.fromEntries(
    Object.keys(r).map((u, l) => [u, i[l]])
  ), c = Y(s, a);
  return B(c);
}
function wo(e) {
  const { init: t, deepEqOnInput: n } = e;
  return n === void 0 ? ce(t ?? Te) : Tt(t ?? Te);
}
function _o(e, t, n) {
  const {
    inputs: r = [],
    code: s,
    data: o,
    asyncInit: i = null,
    deepEqOnInput: a = 0,
    tool: c
  } = e, d = o || Array(r.length).fill(0), u = or(e).map(
    t.getRef
  );
  function l() {
    return r.map((m, y) => {
      if (d[y] === 1)
        return m;
      const w = t.getValue(m);
      return Gn(w) ? w : $t(w);
    });
  }
  const f = mo(c) ?? Y(s), h = a === 0 ? ce(Te) : Tt(Te), p = { immediate: !0, deep: !0 };
  return sr(f) ? (h.value = i, G(
    u,
    async () => {
      l().some(Re) || (h.value = await f(...l()));
    },
    p
  )) : G(
    u,
    () => {
      const m = l();
      m.some(Re) || (h.value = f(...m));
    },
    p
  ), Ct(h);
}
function or(e) {
  const { inputs: t = [], slient: n, data: r } = e, s = n || Array(t.length).fill(0), o = r || Array(t.length).fill(0);
  return t.filter(
    (i, a) => s[a] === 0 && o[a] === 0
  );
}
function Eo(e) {
  const { bind: t = {}, const: n = [] } = e;
  return Object.values(t).filter(
    (r, s) => n[s] === 0
  );
}
function bo(e) {
  const {
    js_computed: t = [],
    vue_computed: n = [],
    binds: r = [],
    id: s
  } = e, o = [], i = [], a = /* @__PURE__ */ new Set(), c = (u, l, f) => {
    for (const h of l) {
      const p = String(h.id);
      a.add(p), o.push({ type: u, item: h });
      for (const m of f(h)) {
        const y = r[m.r];
        y.sid === s && i.push([String(y.id), p]);
      }
    }
  };
  c("js", t, or), c("vue", n, Eo);
  const d = i.filter(([u]) => a.has(u));
  return oo(o, d, (u) => String(u.item.id));
}
function So(e, t, n) {
  const s = {
    ref: {
      r: n.getBindIndex(D(e, t.id))
    },
    type: be.Ref
  };
  return {
    ...t,
    immediate: !0,
    outputs: [s, ...t.outputs || []]
  };
}
function ko(e) {
  const { watchConfigs: t, computedConfigs: n, bindingGetter: r, sid: s } = e;
  return new Ro(t, n, r, s);
}
class Ro {
  constructor(t, n, r, s) {
    T(this, "taskQueue", []);
    T(this, "id2TaskMap", /* @__PURE__ */ new Map());
    T(this, "input2TaskIdMap", Fn(() => []));
    this.bindingGetter = r;
    const o = [], i = (a) => {
      var d;
      const c = new Oo(a, r);
      return this.id2TaskMap.set(c.id, c), (d = a.inputs) == null || d.forEach((u, l) => {
        var h, p;
        if (((h = a.data) == null ? void 0 : h[l]) === 0 && ((p = a.slient) == null ? void 0 : p[l]) === 0) {
          const m = u.r;
          this.input2TaskIdMap.getOrDefault(m).push(c.id);
        }
      }), c;
    };
    t == null || t.forEach((a) => {
      const c = i(a);
      o.push(c);
    }), n == null || n.forEach((a) => {
      const c = i(
        So(s, a, r)
      );
      o.push(c);
    }), o.forEach((a) => {
      const {
        deep: c = !0,
        once: d,
        flush: u,
        immediate: l = !0
      } = a.watchConfig, f = {
        immediate: l,
        deep: c,
        once: d,
        flush: u
      }, h = this._getWatchTargets(a);
      G(
        h,
        (p) => {
          p.some(Re) || (a.modify = !0, this.taskQueue.push(new Po(a)), this._scheduleNextTick());
        },
        f
      );
    });
  }
  _getWatchTargets(t) {
    if (!t.watchConfig.inputs)
      return [];
    const n = t.slientInputs, r = t.constDataInputs;
    return t.watchConfig.inputs.filter(
      (o, i) => !r[i] && !n[i]
    ).map((o) => this.bindingGetter.getRef(o));
  }
  _scheduleNextTick() {
    ke(() => this._runAllTasks());
  }
  _runAllTasks() {
    const t = this.taskQueue.slice();
    this.taskQueue.length = 0, this._setTaskNodeRelations(t), t.forEach((n) => {
      n.run();
    });
  }
  _setTaskNodeRelations(t) {
    t.forEach((n) => {
      const r = this._findNextNodes(n, t);
      n.appendNextNodes(...r), r.forEach((s) => {
        s.appendPrevNodes(n);
      });
    });
  }
  _findNextNodes(t, n) {
    const r = t.watchTask.watchConfig.outputs;
    if (r && r.length <= 0)
      return [];
    const s = this._getCalculatorTasksByOutput(
      t.watchTask.watchConfig.outputs
    );
    return n.filter(
      (o) => s.has(o.watchTask.id) && o.watchTask.id !== t.watchTask.id
    );
  }
  _getCalculatorTasksByOutput(t) {
    const n = /* @__PURE__ */ new Set();
    return t == null || t.forEach((r) => {
      if (!Qn(r.ref))
        return;
      const s = r.ref.r;
      (this.input2TaskIdMap.get(s) || []).forEach((i) => n.add(i));
    }), n;
  }
}
class Oo {
  constructor(t, n) {
    T(this, "modify", !0);
    T(this, "_running", !1);
    T(this, "id");
    T(this, "_runningPromise", null);
    T(this, "_runningPromiseResolve", null);
    T(this, "_inputInfos");
    this.watchConfig = t, this.bindingGetter = n, this.id = Symbol(t.debug), this._inputInfos = this.createInputInfos();
  }
  createInputInfos() {
    const { inputs: t = [] } = this.watchConfig, n = this.watchConfig.data || Array.from({ length: t.length }).fill(0), r = this.watchConfig.slient || Array.from({ length: t.length }).fill(0);
    return {
      const_data: n,
      slients: r
    };
  }
  get slientInputs() {
    return this._inputInfos.slients;
  }
  get constDataInputs() {
    return this._inputInfos.const_data;
  }
  getServerInputs() {
    const { const_data: t } = this._inputInfos;
    return this.watchConfig.inputs ? this.watchConfig.inputs.map((n, r) => t[r] === 0 ? this.bindingGetter.getValue(n) : n) : [];
  }
  get running() {
    return this._running;
  }
  get runningPromise() {
    return this._runningPromise;
  }
  /**
   * setRunning
   */
  setRunning() {
    this._running = !0, this._runningPromise = new Promise((t) => {
      this._runningPromiseResolve = t;
    });
  }
  /**
   * taskDone
   */
  taskDone() {
    this._running = !1, this._runningPromiseResolve && (this._runningPromiseResolve(), this._runningPromiseResolve = null);
  }
}
class Po {
  /**
   *
   */
  constructor(t) {
    T(this, "prevNodes", []);
    T(this, "nextNodes", []);
    T(this, "_runningPrev", !1);
    this.watchTask = t;
  }
  /**
   * appendPrevNodes
   */
  appendPrevNodes(...t) {
    this.prevNodes.push(...t);
  }
  /**
   *
   */
  appendNextNodes(...t) {
    this.nextNodes.push(...t);
  }
  /**
   * hasNextNodes
   */
  hasNextNodes() {
    return this.nextNodes.length > 0;
  }
  /**
   * run
   */
  async run() {
    if (this.prevNodes.length > 0 && !this._runningPrev)
      try {
        this._runningPrev = !0, await Promise.all(this.prevNodes.map((t) => t.run()));
      } finally {
        this._runningPrev = !1;
      }
    if (this.watchTask.running) {
      await this.watchTask.runningPromise;
      return;
    }
    if (this.watchTask.modify) {
      this.watchTask.modify = !1, this.watchTask.setRunning();
      try {
        await No(this.watchTask);
      } finally {
        this.watchTask.taskDone();
      }
    }
  }
}
async function No(e) {
  const { bindingGetter: t } = e, { outputs: n, preSetup: r } = e.watchConfig, s = Bn({
    config: r,
    bindingGetter: t
  });
  try {
    s.run(), e.taskDone();
    const o = await Mn().watchSend(e);
    if (!o)
      return;
    Je(o, n, t);
  } finally {
    s.tryReset();
  }
}
function Vo(e, t) {
  const {
    on: n,
    code: r,
    immediate: s,
    deep: o,
    once: i,
    flush: a,
    bind: c = {},
    onData: d,
    bindData: u
  } = e, l = d || Array.from({ length: n.length }).fill(0), f = u || Array.from({ length: Object.keys(c).length }).fill(0), h = qe(
    c,
    (y, w, _) => f[_] === 0 ? t.getRef(y) : y
  ), p = Y(r, h), m = n.length === 1 ? Qt(l[0] === 1, n[0], t) : n.map(
    (y, w) => Qt(l[w] === 1, y, t)
  );
  return G(m, p, { immediate: s, deep: o, once: i, flush: a });
}
function Qt(e, t, n) {
  return e ? () => t : n.getRef(t);
}
function Co(e, t) {
  const {
    inputs: n = [],
    outputs: r,
    slient: s,
    data: o,
    code: i,
    immediate: a = !0,
    deep: c,
    once: d,
    flush: u
  } = e, l = s || Array.from({ length: n.length }).fill(0), f = o || Array.from({ length: n.length }).fill(0), h = Y(i), p = n.filter((y, w) => l[w] === 0 && f[w] === 0).map((y) => t.getRef(y));
  function m() {
    return n.map((y, w) => {
      if (f[w] === 0) {
        const _ = t.getValue(y);
        return Gn(_) ? _ : $t(_);
      }
      return y;
    });
  }
  G(
    p,
    async () => {
      let y = await h(...m());
      if (!r)
        return;
      const _ = r.length === 1 ? [y] : y, k = _.map((v) => v === void 0 ? 1 : 0);
      Je(
        {
          values: _,
          types: k
        },
        r,
        t
      );
    },
    { immediate: a, deep: c, once: d, flush: u }
  );
}
function Ao() {
  return ir().__VUE_DEVTOOLS_GLOBAL_HOOK__;
}
function ir() {
  return typeof navigator < "u" && typeof window < "u" ? window : typeof globalThis < "u" ? globalThis : {};
}
const xo = typeof Proxy == "function", $o = "devtools-plugin:setup", To = "plugin:settings:set";
let Ee, bt;
function Io() {
  var e;
  return Ee !== void 0 || (typeof window < "u" && window.performance ? (Ee = !0, bt = window.performance) : typeof globalThis < "u" && (!((e = globalThis.perf_hooks) === null || e === void 0) && e.performance) ? (Ee = !0, bt = globalThis.perf_hooks.performance) : Ee = !1), Ee;
}
function Do() {
  return Io() ? bt.now() : Date.now();
}
class Mo {
  constructor(t, n) {
    this.target = null, this.targetQueue = [], this.onQueue = [], this.plugin = t, this.hook = n;
    const r = {};
    if (t.settings)
      for (const i in t.settings) {
        const a = t.settings[i];
        r[i] = a.defaultValue;
      }
    const s = `__vue-devtools-plugin-settings__${t.id}`;
    let o = Object.assign({}, r);
    try {
      const i = localStorage.getItem(s), a = JSON.parse(i);
      Object.assign(o, a);
    } catch {
    }
    this.fallbacks = {
      getSettings() {
        return o;
      },
      setSettings(i) {
        try {
          localStorage.setItem(s, JSON.stringify(i));
        } catch {
        }
        o = i;
      },
      now() {
        return Do();
      }
    }, n && n.on(To, (i, a) => {
      i === this.plugin.id && this.fallbacks.setSettings(a);
    }), this.proxiedOn = new Proxy({}, {
      get: (i, a) => this.target ? this.target.on[a] : (...c) => {
        this.onQueue.push({
          method: a,
          args: c
        });
      }
    }), this.proxiedTarget = new Proxy({}, {
      get: (i, a) => this.target ? this.target[a] : a === "on" ? this.proxiedOn : Object.keys(this.fallbacks).includes(a) ? (...c) => (this.targetQueue.push({
        method: a,
        args: c,
        resolve: () => {
        }
      }), this.fallbacks[a](...c)) : (...c) => new Promise((d) => {
        this.targetQueue.push({
          method: a,
          args: c,
          resolve: d
        });
      })
    });
  }
  async setRealTarget(t) {
    this.target = t;
    for (const n of this.onQueue)
      this.target.on[n.method](...n.args);
    for (const n of this.targetQueue)
      n.resolve(await this.target[n.method](...n.args));
  }
}
function Bo(e, t) {
  const n = e, r = ir(), s = Ao(), o = xo && n.enableEarlyProxy;
  if (s && (r.__VUE_DEVTOOLS_PLUGIN_API_AVAILABLE__ || !o))
    s.emit($o, e, t);
  else {
    const i = o ? new Mo(n, s) : null;
    (r.__VUE_DEVTOOLS_PLUGINS__ = r.__VUE_DEVTOOLS_PLUGINS__ || []).push({
      pluginDescriptor: n,
      setupFn: t,
      proxy: i
    }), i && t(i.proxiedTarget);
  }
}
var O = {};
const ie = typeof document < "u";
function ar(e) {
  return typeof e == "object" || "displayName" in e || "props" in e || "__vccOpts" in e;
}
function jo(e) {
  return e.__esModule || e[Symbol.toStringTag] === "Module" || // support CF with dynamic imports that do not
  // add the Module string tag
  e.default && ar(e.default);
}
const x = Object.assign;
function at(e, t) {
  const n = {};
  for (const r in t) {
    const s = t[r];
    n[r] = ee(s) ? s.map(e) : e(s);
  }
  return n;
}
const xe = () => {
}, ee = Array.isArray;
function P(e) {
  const t = Array.from(arguments).slice(1);
  console.warn.apply(console, ["[Vue Router warn]: " + e].concat(t));
}
const cr = /#/g, Lo = /&/g, Fo = /\//g, Uo = /=/g, Wo = /\?/g, lr = /\+/g, zo = /%5B/g, Ho = /%5D/g, ur = /%5E/g, Ko = /%60/g, fr = /%7B/g, Go = /%7C/g, dr = /%7D/g, qo = /%20/g;
function Mt(e) {
  return encodeURI("" + e).replace(Go, "|").replace(zo, "[").replace(Ho, "]");
}
function Jo(e) {
  return Mt(e).replace(fr, "{").replace(dr, "}").replace(ur, "^");
}
function St(e) {
  return Mt(e).replace(lr, "%2B").replace(qo, "+").replace(cr, "%23").replace(Lo, "%26").replace(Ko, "`").replace(fr, "{").replace(dr, "}").replace(ur, "^");
}
function Qo(e) {
  return St(e).replace(Uo, "%3D");
}
function Yo(e) {
  return Mt(e).replace(cr, "%23").replace(Wo, "%3F");
}
function Xo(e) {
  return e == null ? "" : Yo(e).replace(Fo, "%2F");
}
function Pe(e) {
  try {
    return decodeURIComponent("" + e);
  } catch {
    O.NODE_ENV !== "production" && P(`Error decoding "${e}". Using original value`);
  }
  return "" + e;
}
const Zo = /\/$/, ei = (e) => e.replace(Zo, "");
function ct(e, t, n = "/") {
  let r, s = {}, o = "", i = "";
  const a = t.indexOf("#");
  let c = t.indexOf("?");
  return a < c && a >= 0 && (c = -1), c > -1 && (r = t.slice(0, c), o = t.slice(c + 1, a > -1 ? a : t.length), s = e(o)), a > -1 && (r = r || t.slice(0, a), i = t.slice(a, t.length)), r = ri(r ?? t, n), {
    fullPath: r + (o && "?") + o + i,
    path: r,
    query: s,
    hash: Pe(i)
  };
}
function ti(e, t) {
  const n = t.query ? e(t.query) : "";
  return t.path + (n && "?") + n + (t.hash || "");
}
function Yt(e, t) {
  return !t || !e.toLowerCase().startsWith(t.toLowerCase()) ? e : e.slice(t.length) || "/";
}
function Xt(e, t, n) {
  const r = t.matched.length - 1, s = n.matched.length - 1;
  return r > -1 && r === s && pe(t.matched[r], n.matched[s]) && hr(t.params, n.params) && e(t.query) === e(n.query) && t.hash === n.hash;
}
function pe(e, t) {
  return (e.aliasOf || e) === (t.aliasOf || t);
}
function hr(e, t) {
  if (Object.keys(e).length !== Object.keys(t).length)
    return !1;
  for (const n in e)
    if (!ni(e[n], t[n]))
      return !1;
  return !0;
}
function ni(e, t) {
  return ee(e) ? Zt(e, t) : ee(t) ? Zt(t, e) : e === t;
}
function Zt(e, t) {
  return ee(t) ? e.length === t.length && e.every((n, r) => n === t[r]) : e.length === 1 && e[0] === t;
}
function ri(e, t) {
  if (e.startsWith("/"))
    return e;
  if (O.NODE_ENV !== "production" && !t.startsWith("/"))
    return P(`Cannot resolve a relative location without an absolute path. Trying to resolve "${e}" from "${t}". It should look like "/${t}".`), e;
  if (!e)
    return t;
  const n = t.split("/"), r = e.split("/"), s = r[r.length - 1];
  (s === ".." || s === ".") && r.push("");
  let o = n.length - 1, i, a;
  for (i = 0; i < r.length; i++)
    if (a = r[i], a !== ".")
      if (a === "..")
        o > 1 && o--;
      else
        break;
  return n.slice(0, o).join("/") + "/" + r.slice(i).join("/");
}
const ue = {
  path: "/",
  // TODO: could we use a symbol in the future?
  name: void 0,
  params: {},
  query: {},
  hash: "",
  fullPath: "/",
  matched: [],
  meta: {},
  redirectedFrom: void 0
};
var Ne;
(function(e) {
  e.pop = "pop", e.push = "push";
})(Ne || (Ne = {}));
var ve;
(function(e) {
  e.back = "back", e.forward = "forward", e.unknown = "";
})(ve || (ve = {}));
const lt = "";
function pr(e) {
  if (!e)
    if (ie) {
      const t = document.querySelector("base");
      e = t && t.getAttribute("href") || "/", e = e.replace(/^\w+:\/\/[^\/]+/, "");
    } else
      e = "/";
  return e[0] !== "/" && e[0] !== "#" && (e = "/" + e), ei(e);
}
const si = /^[^#]+#/;
function mr(e, t) {
  return e.replace(si, "#") + t;
}
function oi(e, t) {
  const n = document.documentElement.getBoundingClientRect(), r = e.getBoundingClientRect();
  return {
    behavior: t.behavior,
    left: r.left - n.left - (t.left || 0),
    top: r.top - n.top - (t.top || 0)
  };
}
const Qe = () => ({
  left: window.scrollX,
  top: window.scrollY
});
function ii(e) {
  let t;
  if ("el" in e) {
    const n = e.el, r = typeof n == "string" && n.startsWith("#");
    if (O.NODE_ENV !== "production" && typeof e.el == "string" && (!r || !document.getElementById(e.el.slice(1))))
      try {
        const o = document.querySelector(e.el);
        if (r && o) {
          P(`The selector "${e.el}" should be passed as "el: document.querySelector('${e.el}')" because it starts with "#".`);
          return;
        }
      } catch {
        P(`The selector "${e.el}" is invalid. If you are using an id selector, make sure to escape it. You can find more information about escaping characters in selectors at https://mathiasbynens.be/notes/css-escapes or use CSS.escape (https://developer.mozilla.org/en-US/docs/Web/API/CSS/escape).`);
        return;
      }
    const s = typeof n == "string" ? r ? document.getElementById(n.slice(1)) : document.querySelector(n) : n;
    if (!s) {
      O.NODE_ENV !== "production" && P(`Couldn't find element using selector "${e.el}" returned by scrollBehavior.`);
      return;
    }
    t = oi(s, e);
  } else
    t = e;
  "scrollBehavior" in document.documentElement.style ? window.scrollTo(t) : window.scrollTo(t.left != null ? t.left : window.scrollX, t.top != null ? t.top : window.scrollY);
}
function en(e, t) {
  return (history.state ? history.state.position - t : -1) + e;
}
const kt = /* @__PURE__ */ new Map();
function ai(e, t) {
  kt.set(e, t);
}
function ci(e) {
  const t = kt.get(e);
  return kt.delete(e), t;
}
let li = () => location.protocol + "//" + location.host;
function gr(e, t) {
  const { pathname: n, search: r, hash: s } = t, o = e.indexOf("#");
  if (o > -1) {
    let a = s.includes(e.slice(o)) ? e.slice(o).length : 1, c = s.slice(a);
    return c[0] !== "/" && (c = "/" + c), Yt(c, "");
  }
  return Yt(n, e) + r + s;
}
function ui(e, t, n, r) {
  let s = [], o = [], i = null;
  const a = ({ state: f }) => {
    const h = gr(e, location), p = n.value, m = t.value;
    let y = 0;
    if (f) {
      if (n.value = h, t.value = f, i && i === p) {
        i = null;
        return;
      }
      y = m ? f.position - m.position : 0;
    } else
      r(h);
    s.forEach((w) => {
      w(n.value, p, {
        delta: y,
        type: Ne.pop,
        direction: y ? y > 0 ? ve.forward : ve.back : ve.unknown
      });
    });
  };
  function c() {
    i = n.value;
  }
  function d(f) {
    s.push(f);
    const h = () => {
      const p = s.indexOf(f);
      p > -1 && s.splice(p, 1);
    };
    return o.push(h), h;
  }
  function u() {
    const { history: f } = window;
    f.state && f.replaceState(x({}, f.state, { scroll: Qe() }), "");
  }
  function l() {
    for (const f of o)
      f();
    o = [], window.removeEventListener("popstate", a), window.removeEventListener("beforeunload", u);
  }
  return window.addEventListener("popstate", a), window.addEventListener("beforeunload", u, {
    passive: !0
  }), {
    pauseListeners: c,
    listen: d,
    destroy: l
  };
}
function tn(e, t, n, r = !1, s = !1) {
  return {
    back: e,
    current: t,
    forward: n,
    replaced: r,
    position: window.history.length,
    scroll: s ? Qe() : null
  };
}
function fi(e) {
  const { history: t, location: n } = window, r = {
    value: gr(e, n)
  }, s = { value: t.state };
  s.value || o(r.value, {
    back: null,
    current: r.value,
    forward: null,
    // the length is off by one, we need to decrease it
    position: t.length - 1,
    replaced: !0,
    // don't add a scroll as the user may have an anchor, and we want
    // scrollBehavior to be triggered without a saved position
    scroll: null
  }, !0);
  function o(c, d, u) {
    const l = e.indexOf("#"), f = l > -1 ? (n.host && document.querySelector("base") ? e : e.slice(l)) + c : li() + e + c;
    try {
      t[u ? "replaceState" : "pushState"](d, "", f), s.value = d;
    } catch (h) {
      O.NODE_ENV !== "production" ? P("Error with push/replace State", h) : console.error(h), n[u ? "replace" : "assign"](f);
    }
  }
  function i(c, d) {
    const u = x({}, t.state, tn(
      s.value.back,
      // keep back and forward entries but override current position
      c,
      s.value.forward,
      !0
    ), d, { position: s.value.position });
    o(c, u, !0), r.value = c;
  }
  function a(c, d) {
    const u = x(
      {},
      // use current history state to gracefully handle a wrong call to
      // history.replaceState
      // https://github.com/vuejs/router/issues/366
      s.value,
      t.state,
      {
        forward: c,
        scroll: Qe()
      }
    );
    O.NODE_ENV !== "production" && !t.state && P(`history.state seems to have been manually replaced without preserving the necessary values. Make sure to preserve existing history state if you are manually calling history.replaceState:

history.replaceState(history.state, '', url)

You can find more information at https://router.vuejs.org/guide/migration/#Usage-of-history-state`), o(u.current, u, !0);
    const l = x({}, tn(r.value, c, null), { position: u.position + 1 }, d);
    o(c, l, !1), r.value = c;
  }
  return {
    location: r,
    state: s,
    push: a,
    replace: i
  };
}
function yr(e) {
  e = pr(e);
  const t = fi(e), n = ui(e, t.state, t.location, t.replace);
  function r(o, i = !0) {
    i || n.pauseListeners(), history.go(o);
  }
  const s = x({
    // it's overridden right after
    location: "",
    base: e,
    go: r,
    createHref: mr.bind(null, e)
  }, t, n);
  return Object.defineProperty(s, "location", {
    enumerable: !0,
    get: () => t.location.value
  }), Object.defineProperty(s, "state", {
    enumerable: !0,
    get: () => t.state.value
  }), s;
}
function di(e = "") {
  let t = [], n = [lt], r = 0;
  e = pr(e);
  function s(a) {
    r++, r !== n.length && n.splice(r), n.push(a);
  }
  function o(a, c, { direction: d, delta: u }) {
    const l = {
      direction: d,
      delta: u,
      type: Ne.pop
    };
    for (const f of t)
      f(a, c, l);
  }
  const i = {
    // rewritten by Object.defineProperty
    location: lt,
    // TODO: should be kept in queue
    state: {},
    base: e,
    createHref: mr.bind(null, e),
    replace(a) {
      n.splice(r--, 1), s(a);
    },
    push(a, c) {
      s(a);
    },
    listen(a) {
      return t.push(a), () => {
        const c = t.indexOf(a);
        c > -1 && t.splice(c, 1);
      };
    },
    destroy() {
      t = [], n = [lt], r = 0;
    },
    go(a, c = !0) {
      const d = this.location, u = (
        // we are considering delta === 0 going forward, but in abstract mode
        // using 0 for the delta doesn't make sense like it does in html5 where
        // it reloads the page
        a < 0 ? ve.back : ve.forward
      );
      r = Math.max(0, Math.min(r + a, n.length - 1)), c && o(this.location, d, {
        direction: u,
        delta: a
      });
    }
  };
  return Object.defineProperty(i, "location", {
    enumerable: !0,
    get: () => n[r]
  }), i;
}
function hi(e) {
  return e = location.host ? e || location.pathname + location.search : "", e.includes("#") || (e += "#"), O.NODE_ENV !== "production" && !e.endsWith("#/") && !e.endsWith("#") && P(`A hash base must end with a "#":
"${e}" should be "${e.replace(/#.*$/, "#")}".`), yr(e);
}
function Ke(e) {
  return typeof e == "string" || e && typeof e == "object";
}
function vr(e) {
  return typeof e == "string" || typeof e == "symbol";
}
const Rt = Symbol(O.NODE_ENV !== "production" ? "navigation failure" : "");
var nn;
(function(e) {
  e[e.aborted = 4] = "aborted", e[e.cancelled = 8] = "cancelled", e[e.duplicated = 16] = "duplicated";
})(nn || (nn = {}));
const pi = {
  1({ location: e, currentLocation: t }) {
    return `No match for
 ${JSON.stringify(e)}${t ? `
while being at
` + JSON.stringify(t) : ""}`;
  },
  2({ from: e, to: t }) {
    return `Redirected from "${e.fullPath}" to "${gi(t)}" via a navigation guard.`;
  },
  4({ from: e, to: t }) {
    return `Navigation aborted from "${e.fullPath}" to "${t.fullPath}" via a navigation guard.`;
  },
  8({ from: e, to: t }) {
    return `Navigation cancelled from "${e.fullPath}" to "${t.fullPath}" with a new navigation.`;
  },
  16({ from: e, to: t }) {
    return `Avoided redundant navigation to current location: "${e.fullPath}".`;
  }
};
function Ve(e, t) {
  return O.NODE_ENV !== "production" ? x(new Error(pi[e](t)), {
    type: e,
    [Rt]: !0
  }, t) : x(new Error(), {
    type: e,
    [Rt]: !0
  }, t);
}
function oe(e, t) {
  return e instanceof Error && Rt in e && (t == null || !!(e.type & t));
}
const mi = ["params", "query", "hash"];
function gi(e) {
  if (typeof e == "string")
    return e;
  if (e.path != null)
    return e.path;
  const t = {};
  for (const n of mi)
    n in e && (t[n] = e[n]);
  return JSON.stringify(t, null, 2);
}
const rn = "[^/]+?", yi = {
  sensitive: !1,
  strict: !1,
  start: !0,
  end: !0
}, vi = /[.+*?^${}()[\]/\\]/g;
function wi(e, t) {
  const n = x({}, yi, t), r = [];
  let s = n.start ? "^" : "";
  const o = [];
  for (const d of e) {
    const u = d.length ? [] : [
      90
      /* PathScore.Root */
    ];
    n.strict && !d.length && (s += "/");
    for (let l = 0; l < d.length; l++) {
      const f = d[l];
      let h = 40 + (n.sensitive ? 0.25 : 0);
      if (f.type === 0)
        l || (s += "/"), s += f.value.replace(vi, "\\$&"), h += 40;
      else if (f.type === 1) {
        const { value: p, repeatable: m, optional: y, regexp: w } = f;
        o.push({
          name: p,
          repeatable: m,
          optional: y
        });
        const _ = w || rn;
        if (_ !== rn) {
          h += 10;
          try {
            new RegExp(`(${_})`);
          } catch (v) {
            throw new Error(`Invalid custom RegExp for param "${p}" (${_}): ` + v.message);
          }
        }
        let k = m ? `((?:${_})(?:/(?:${_}))*)` : `(${_})`;
        l || (k = // avoid an optional / if there are more segments e.g. /:p?-static
        // or /:p?-:p2
        y && d.length < 2 ? `(?:/${k})` : "/" + k), y && (k += "?"), s += k, h += 20, y && (h += -8), m && (h += -20), _ === ".*" && (h += -50);
      }
      u.push(h);
    }
    r.push(u);
  }
  if (n.strict && n.end) {
    const d = r.length - 1;
    r[d][r[d].length - 1] += 0.7000000000000001;
  }
  n.strict || (s += "/?"), n.end ? s += "$" : n.strict && !s.endsWith("/") && (s += "(?:/|$)");
  const i = new RegExp(s, n.sensitive ? "" : "i");
  function a(d) {
    const u = d.match(i), l = {};
    if (!u)
      return null;
    for (let f = 1; f < u.length; f++) {
      const h = u[f] || "", p = o[f - 1];
      l[p.name] = h && p.repeatable ? h.split("/") : h;
    }
    return l;
  }
  function c(d) {
    let u = "", l = !1;
    for (const f of e) {
      (!l || !u.endsWith("/")) && (u += "/"), l = !1;
      for (const h of f)
        if (h.type === 0)
          u += h.value;
        else if (h.type === 1) {
          const { value: p, repeatable: m, optional: y } = h, w = p in d ? d[p] : "";
          if (ee(w) && !m)
            throw new Error(`Provided param "${p}" is an array but it is not repeatable (* or + modifiers)`);
          const _ = ee(w) ? w.join("/") : w;
          if (!_)
            if (y)
              f.length < 2 && (u.endsWith("/") ? u = u.slice(0, -1) : l = !0);
            else
              throw new Error(`Missing required param "${p}"`);
          u += _;
        }
    }
    return u || "/";
  }
  return {
    re: i,
    score: r,
    keys: o,
    parse: a,
    stringify: c
  };
}
function _i(e, t) {
  let n = 0;
  for (; n < e.length && n < t.length; ) {
    const r = t[n] - e[n];
    if (r)
      return r;
    n++;
  }
  return e.length < t.length ? e.length === 1 && e[0] === 80 ? -1 : 1 : e.length > t.length ? t.length === 1 && t[0] === 80 ? 1 : -1 : 0;
}
function wr(e, t) {
  let n = 0;
  const r = e.score, s = t.score;
  for (; n < r.length && n < s.length; ) {
    const o = _i(r[n], s[n]);
    if (o)
      return o;
    n++;
  }
  if (Math.abs(s.length - r.length) === 1) {
    if (sn(r))
      return 1;
    if (sn(s))
      return -1;
  }
  return s.length - r.length;
}
function sn(e) {
  const t = e[e.length - 1];
  return e.length > 0 && t[t.length - 1] < 0;
}
const Ei = {
  type: 0,
  value: ""
}, bi = /[a-zA-Z0-9_]/;
function Si(e) {
  if (!e)
    return [[]];
  if (e === "/")
    return [[Ei]];
  if (!e.startsWith("/"))
    throw new Error(O.NODE_ENV !== "production" ? `Route paths should start with a "/": "${e}" should be "/${e}".` : `Invalid path "${e}"`);
  function t(h) {
    throw new Error(`ERR (${n})/"${d}": ${h}`);
  }
  let n = 0, r = n;
  const s = [];
  let o;
  function i() {
    o && s.push(o), o = [];
  }
  let a = 0, c, d = "", u = "";
  function l() {
    d && (n === 0 ? o.push({
      type: 0,
      value: d
    }) : n === 1 || n === 2 || n === 3 ? (o.length > 1 && (c === "*" || c === "+") && t(`A repeatable param (${d}) must be alone in its segment. eg: '/:ids+.`), o.push({
      type: 1,
      value: d,
      regexp: u,
      repeatable: c === "*" || c === "+",
      optional: c === "*" || c === "?"
    })) : t("Invalid state to consume buffer"), d = "");
  }
  function f() {
    d += c;
  }
  for (; a < e.length; ) {
    if (c = e[a++], c === "\\" && n !== 2) {
      r = n, n = 4;
      continue;
    }
    switch (n) {
      case 0:
        c === "/" ? (d && l(), i()) : c === ":" ? (l(), n = 1) : f();
        break;
      case 4:
        f(), n = r;
        break;
      case 1:
        c === "(" ? n = 2 : bi.test(c) ? f() : (l(), n = 0, c !== "*" && c !== "?" && c !== "+" && a--);
        break;
      case 2:
        c === ")" ? u[u.length - 1] == "\\" ? u = u.slice(0, -1) + c : n = 3 : u += c;
        break;
      case 3:
        l(), n = 0, c !== "*" && c !== "?" && c !== "+" && a--, u = "";
        break;
      default:
        t("Unknown state");
        break;
    }
  }
  return n === 2 && t(`Unfinished custom RegExp for param "${d}"`), l(), i(), s;
}
function ki(e, t, n) {
  const r = wi(Si(e.path), n);
  if (O.NODE_ENV !== "production") {
    const o = /* @__PURE__ */ new Set();
    for (const i of r.keys)
      o.has(i.name) && P(`Found duplicated params with name "${i.name}" for path "${e.path}". Only the last one will be available on "$route.params".`), o.add(i.name);
  }
  const s = x(r, {
    record: e,
    parent: t,
    // these needs to be populated by the parent
    children: [],
    alias: []
  });
  return t && !s.record.aliasOf == !t.record.aliasOf && t.children.push(s), s;
}
function Ri(e, t) {
  const n = [], r = /* @__PURE__ */ new Map();
  t = ln({ strict: !1, end: !0, sensitive: !1 }, t);
  function s(l) {
    return r.get(l);
  }
  function o(l, f, h) {
    const p = !h, m = an(l);
    O.NODE_ENV !== "production" && Vi(m, f), m.aliasOf = h && h.record;
    const y = ln(t, l), w = [m];
    if ("alias" in l) {
      const v = typeof l.alias == "string" ? [l.alias] : l.alias;
      for (const R of v)
        w.push(
          // we need to normalize again to ensure the `mods` property
          // being non enumerable
          an(x({}, m, {
            // this allows us to hold a copy of the `components` option
            // so that async components cache is hold on the original record
            components: h ? h.record.components : m.components,
            path: R,
            // we might be the child of an alias
            aliasOf: h ? h.record : m
            // the aliases are always of the same kind as the original since they
            // are defined on the same record
          }))
        );
    }
    let _, k;
    for (const v of w) {
      const { path: R } = v;
      if (f && R[0] !== "/") {
        const A = f.record.path, I = A[A.length - 1] === "/" ? "" : "/";
        v.path = f.record.path + (R && I + R);
      }
      if (O.NODE_ENV !== "production" && v.path === "*")
        throw new Error(`Catch all routes ("*") must now be defined using a param with a custom regexp.
See more at https://router.vuejs.org/guide/migration/#Removed-star-or-catch-all-routes.`);
      if (_ = ki(v, f, y), O.NODE_ENV !== "production" && f && R[0] === "/" && Ai(_, f), h ? (h.alias.push(_), O.NODE_ENV !== "production" && Ni(h, _)) : (k = k || _, k !== _ && k.alias.push(_), p && l.name && !cn(_) && (O.NODE_ENV !== "production" && Ci(l, f), i(l.name))), _r(_) && c(_), m.children) {
        const A = m.children;
        for (let I = 0; I < A.length; I++)
          o(A[I], _, h && h.children[I]);
      }
      h = h || _;
    }
    return k ? () => {
      i(k);
    } : xe;
  }
  function i(l) {
    if (vr(l)) {
      const f = r.get(l);
      f && (r.delete(l), n.splice(n.indexOf(f), 1), f.children.forEach(i), f.alias.forEach(i));
    } else {
      const f = n.indexOf(l);
      f > -1 && (n.splice(f, 1), l.record.name && r.delete(l.record.name), l.children.forEach(i), l.alias.forEach(i));
    }
  }
  function a() {
    return n;
  }
  function c(l) {
    const f = xi(l, n);
    n.splice(f, 0, l), l.record.name && !cn(l) && r.set(l.record.name, l);
  }
  function d(l, f) {
    let h, p = {}, m, y;
    if ("name" in l && l.name) {
      if (h = r.get(l.name), !h)
        throw Ve(1, {
          location: l
        });
      if (O.NODE_ENV !== "production") {
        const k = Object.keys(l.params || {}).filter((v) => !h.keys.find((R) => R.name === v));
        k.length && P(`Discarded invalid param(s) "${k.join('", "')}" when navigating. See https://github.com/vuejs/router/blob/main/packages/router/CHANGELOG.md#414-2022-08-22 for more details.`);
      }
      y = h.record.name, p = x(
        // paramsFromLocation is a new object
        on(
          f.params,
          // only keep params that exist in the resolved location
          // only keep optional params coming from a parent record
          h.keys.filter((k) => !k.optional).concat(h.parent ? h.parent.keys.filter((k) => k.optional) : []).map((k) => k.name)
        ),
        // discard any existing params in the current location that do not exist here
        // #1497 this ensures better active/exact matching
        l.params && on(l.params, h.keys.map((k) => k.name))
      ), m = h.stringify(p);
    } else if (l.path != null)
      m = l.path, O.NODE_ENV !== "production" && !m.startsWith("/") && P(`The Matcher cannot resolve relative paths but received "${m}". Unless you directly called \`matcher.resolve("${m}")\`, this is probably a bug in vue-router. Please open an issue at https://github.com/vuejs/router/issues/new/choose.`), h = n.find((k) => k.re.test(m)), h && (p = h.parse(m), y = h.record.name);
    else {
      if (h = f.name ? r.get(f.name) : n.find((k) => k.re.test(f.path)), !h)
        throw Ve(1, {
          location: l,
          currentLocation: f
        });
      y = h.record.name, p = x({}, f.params, l.params), m = h.stringify(p);
    }
    const w = [];
    let _ = h;
    for (; _; )
      w.unshift(_.record), _ = _.parent;
    return {
      name: y,
      path: m,
      params: p,
      matched: w,
      meta: Pi(w)
    };
  }
  e.forEach((l) => o(l));
  function u() {
    n.length = 0, r.clear();
  }
  return {
    addRoute: o,
    resolve: d,
    removeRoute: i,
    clearRoutes: u,
    getRoutes: a,
    getRecordMatcher: s
  };
}
function on(e, t) {
  const n = {};
  for (const r of t)
    r in e && (n[r] = e[r]);
  return n;
}
function an(e) {
  const t = {
    path: e.path,
    redirect: e.redirect,
    name: e.name,
    meta: e.meta || {},
    aliasOf: e.aliasOf,
    beforeEnter: e.beforeEnter,
    props: Oi(e),
    children: e.children || [],
    instances: {},
    leaveGuards: /* @__PURE__ */ new Set(),
    updateGuards: /* @__PURE__ */ new Set(),
    enterCallbacks: {},
    // must be declared afterwards
    // mods: {},
    components: "components" in e ? e.components || null : e.component && { default: e.component }
  };
  return Object.defineProperty(t, "mods", {
    value: {}
  }), t;
}
function Oi(e) {
  const t = {}, n = e.props || !1;
  if ("component" in e)
    t.default = n;
  else
    for (const r in e.components)
      t[r] = typeof n == "object" ? n[r] : n;
  return t;
}
function cn(e) {
  for (; e; ) {
    if (e.record.aliasOf)
      return !0;
    e = e.parent;
  }
  return !1;
}
function Pi(e) {
  return e.reduce((t, n) => x(t, n.meta), {});
}
function ln(e, t) {
  const n = {};
  for (const r in e)
    n[r] = r in t ? t[r] : e[r];
  return n;
}
function Ot(e, t) {
  return e.name === t.name && e.optional === t.optional && e.repeatable === t.repeatable;
}
function Ni(e, t) {
  for (const n of e.keys)
    if (!n.optional && !t.keys.find(Ot.bind(null, n)))
      return P(`Alias "${t.record.path}" and the original record: "${e.record.path}" must have the exact same param named "${n.name}"`);
  for (const n of t.keys)
    if (!n.optional && !e.keys.find(Ot.bind(null, n)))
      return P(`Alias "${t.record.path}" and the original record: "${e.record.path}" must have the exact same param named "${n.name}"`);
}
function Vi(e, t) {
  t && t.record.name && !e.name && !e.path && P(`The route named "${String(t.record.name)}" has a child without a name and an empty path. Using that name won't render the empty path child so you probably want to move the name to the child instead. If this is intentional, add a name to the child route to remove the warning.`);
}
function Ci(e, t) {
  for (let n = t; n; n = n.parent)
    if (n.record.name === e.name)
      throw new Error(`A route named "${String(e.name)}" has been added as a ${t === n ? "child" : "descendant"} of a route with the same name. Route names must be unique and a nested route cannot use the same name as an ancestor.`);
}
function Ai(e, t) {
  for (const n of t.keys)
    if (!e.keys.find(Ot.bind(null, n)))
      return P(`Absolute path "${e.record.path}" must have the exact same param named "${n.name}" as its parent "${t.record.path}".`);
}
function xi(e, t) {
  let n = 0, r = t.length;
  for (; n !== r; ) {
    const o = n + r >> 1;
    wr(e, t[o]) < 0 ? r = o : n = o + 1;
  }
  const s = $i(e);
  return s && (r = t.lastIndexOf(s, r - 1), O.NODE_ENV !== "production" && r < 0 && P(`Finding ancestor route "${s.record.path}" failed for "${e.record.path}"`)), r;
}
function $i(e) {
  let t = e;
  for (; t = t.parent; )
    if (_r(t) && wr(e, t) === 0)
      return t;
}
function _r({ record: e }) {
  return !!(e.name || e.components && Object.keys(e.components).length || e.redirect);
}
function Ti(e) {
  const t = {};
  if (e === "" || e === "?")
    return t;
  const r = (e[0] === "?" ? e.slice(1) : e).split("&");
  for (let s = 0; s < r.length; ++s) {
    const o = r[s].replace(lr, " "), i = o.indexOf("="), a = Pe(i < 0 ? o : o.slice(0, i)), c = i < 0 ? null : Pe(o.slice(i + 1));
    if (a in t) {
      let d = t[a];
      ee(d) || (d = t[a] = [d]), d.push(c);
    } else
      t[a] = c;
  }
  return t;
}
function un(e) {
  let t = "";
  for (let n in e) {
    const r = e[n];
    if (n = Qo(n), r == null) {
      r !== void 0 && (t += (t.length ? "&" : "") + n);
      continue;
    }
    (ee(r) ? r.map((o) => o && St(o)) : [r && St(r)]).forEach((o) => {
      o !== void 0 && (t += (t.length ? "&" : "") + n, o != null && (t += "=" + o));
    });
  }
  return t;
}
function Ii(e) {
  const t = {};
  for (const n in e) {
    const r = e[n];
    r !== void 0 && (t[n] = ee(r) ? r.map((s) => s == null ? null : "" + s) : r == null ? r : "" + r);
  }
  return t;
}
const Di = Symbol(O.NODE_ENV !== "production" ? "router view location matched" : ""), fn = Symbol(O.NODE_ENV !== "production" ? "router view depth" : ""), Ye = Symbol(O.NODE_ENV !== "production" ? "router" : ""), Bt = Symbol(O.NODE_ENV !== "production" ? "route location" : ""), Pt = Symbol(O.NODE_ENV !== "production" ? "router view location" : "");
function Ce() {
  let e = [];
  function t(r) {
    return e.push(r), () => {
      const s = e.indexOf(r);
      s > -1 && e.splice(s, 1);
    };
  }
  function n() {
    e = [];
  }
  return {
    add: t,
    list: () => e.slice(),
    reset: n
  };
}
function fe(e, t, n, r, s, o = (i) => i()) {
  const i = r && // name is defined if record is because of the function overload
  (r.enterCallbacks[s] = r.enterCallbacks[s] || []);
  return () => new Promise((a, c) => {
    const d = (f) => {
      f === !1 ? c(Ve(4, {
        from: n,
        to: t
      })) : f instanceof Error ? c(f) : Ke(f) ? c(Ve(2, {
        from: t,
        to: f
      })) : (i && // since enterCallbackArray is truthy, both record and name also are
      r.enterCallbacks[s] === i && typeof f == "function" && i.push(f), a());
    }, u = o(() => e.call(r && r.instances[s], t, n, O.NODE_ENV !== "production" ? Mi(d, t, n) : d));
    let l = Promise.resolve(u);
    if (e.length < 3 && (l = l.then(d)), O.NODE_ENV !== "production" && e.length > 2) {
      const f = `The "next" callback was never called inside of ${e.name ? '"' + e.name + '"' : ""}:
${e.toString()}
. If you are returning a value instead of calling "next", make sure to remove the "next" parameter from your function.`;
      if (typeof u == "object" && "then" in u)
        l = l.then((h) => d._called ? h : (P(f), Promise.reject(new Error("Invalid navigation guard"))));
      else if (u !== void 0 && !d._called) {
        P(f), c(new Error("Invalid navigation guard"));
        return;
      }
    }
    l.catch((f) => c(f));
  });
}
function Mi(e, t, n) {
  let r = 0;
  return function() {
    r++ === 1 && P(`The "next" callback was called more than once in one navigation guard when going from "${n.fullPath}" to "${t.fullPath}". It should be called exactly one time in each navigation guard. This will fail in production.`), e._called = !0, r === 1 && e.apply(null, arguments);
  };
}
function ut(e, t, n, r, s = (o) => o()) {
  const o = [];
  for (const i of e) {
    O.NODE_ENV !== "production" && !i.components && !i.children.length && P(`Record with path "${i.path}" is either missing a "component(s)" or "children" property.`);
    for (const a in i.components) {
      let c = i.components[a];
      if (O.NODE_ENV !== "production") {
        if (!c || typeof c != "object" && typeof c != "function")
          throw P(`Component "${a}" in record with path "${i.path}" is not a valid component. Received "${String(c)}".`), new Error("Invalid route component");
        if ("then" in c) {
          P(`Component "${a}" in record with path "${i.path}" is a Promise instead of a function that returns a Promise. Did you write "import('./MyPage.vue')" instead of "() => import('./MyPage.vue')" ? This will break in production if not fixed.`);
          const d = c;
          c = () => d;
        } else c.__asyncLoader && // warn only once per component
        !c.__warnedDefineAsync && (c.__warnedDefineAsync = !0, P(`Component "${a}" in record with path "${i.path}" is defined using "defineAsyncComponent()". Write "() => import('./MyPage.vue')" instead of "defineAsyncComponent(() => import('./MyPage.vue'))".`));
      }
      if (!(t !== "beforeRouteEnter" && !i.instances[a]))
        if (ar(c)) {
          const u = (c.__vccOpts || c)[t];
          u && o.push(fe(u, n, r, i, a, s));
        } else {
          let d = c();
          O.NODE_ENV !== "production" && !("catch" in d) && (P(`Component "${a}" in record with path "${i.path}" is a function that does not return a Promise. If you were passing a functional component, make sure to add a "displayName" to the component. This will break in production if not fixed.`), d = Promise.resolve(d)), o.push(() => d.then((u) => {
            if (!u)
              throw new Error(`Couldn't resolve component "${a}" at "${i.path}"`);
            const l = jo(u) ? u.default : u;
            i.mods[a] = u, i.components[a] = l;
            const h = (l.__vccOpts || l)[t];
            return h && fe(h, n, r, i, a, s)();
          }));
        }
    }
  }
  return o;
}
function dn(e) {
  const t = le(Ye), n = le(Bt);
  let r = !1, s = null;
  const o = B(() => {
    const u = Q(e.to);
    return O.NODE_ENV !== "production" && (!r || u !== s) && (Ke(u) || (r ? P(`Invalid value for prop "to" in useLink()
- to:`, u, `
- previous to:`, s, `
- props:`, e) : P(`Invalid value for prop "to" in useLink()
- to:`, u, `
- props:`, e)), s = u, r = !0), t.resolve(u);
  }), i = B(() => {
    const { matched: u } = o.value, { length: l } = u, f = u[l - 1], h = n.matched;
    if (!f || !h.length)
      return -1;
    const p = h.findIndex(pe.bind(null, f));
    if (p > -1)
      return p;
    const m = hn(u[l - 2]);
    return (
      // we are dealing with nested routes
      l > 1 && // if the parent and matched route have the same path, this link is
      // referring to the empty child. Or we currently are on a different
      // child of the same parent
      hn(f) === m && // avoid comparing the child with its parent
      h[h.length - 1].path !== m ? h.findIndex(pe.bind(null, u[l - 2])) : p
    );
  }), a = B(() => i.value > -1 && Ui(n.params, o.value.params)), c = B(() => i.value > -1 && i.value === n.matched.length - 1 && hr(n.params, o.value.params));
  function d(u = {}) {
    if (Fi(u)) {
      const l = t[Q(e.replace) ? "replace" : "push"](
        Q(e.to)
        // avoid uncaught errors are they are logged anyway
      ).catch(xe);
      return e.viewTransition && typeof document < "u" && "startViewTransition" in document && document.startViewTransition(() => l), l;
    }
    return Promise.resolve();
  }
  if (O.NODE_ENV !== "production" && ie) {
    const u = Ge();
    if (u) {
      const l = {
        route: o.value,
        isActive: a.value,
        isExactActive: c.value,
        error: null
      };
      u.__vrl_devtools = u.__vrl_devtools || [], u.__vrl_devtools.push(l), xt(() => {
        l.route = o.value, l.isActive = a.value, l.isExactActive = c.value, l.error = Ke(Q(e.to)) ? null : 'Invalid "to" value';
      }, { flush: "post" });
    }
  }
  return {
    route: o,
    href: B(() => o.value.href),
    isActive: a,
    isExactActive: c,
    navigate: d
  };
}
function Bi(e) {
  return e.length === 1 ? e[0] : e;
}
const ji = /* @__PURE__ */ X({
  name: "RouterLink",
  compatConfig: { MODE: 3 },
  props: {
    to: {
      type: [String, Object],
      required: !0
    },
    replace: Boolean,
    activeClass: String,
    // inactiveClass: String,
    exactActiveClass: String,
    custom: Boolean,
    ariaCurrentValue: {
      type: String,
      default: "page"
    }
  },
  useLink: dn,
  setup(e, { slots: t }) {
    const n = Kr(dn(e)), { options: r } = le(Ye), s = B(() => ({
      [pn(e.activeClass, r.linkActiveClass, "router-link-active")]: n.isActive,
      // [getLinkClass(
      //   props.inactiveClass,
      //   options.linkInactiveClass,
      //   'router-link-inactive'
      // )]: !link.isExactActive,
      [pn(e.exactActiveClass, r.linkExactActiveClass, "router-link-exact-active")]: n.isExactActive
    }));
    return () => {
      const o = t.default && Bi(t.default(n));
      return e.custom ? o : q("a", {
        "aria-current": n.isExactActive ? e.ariaCurrentValue : null,
        href: n.href,
        // this would override user added attrs but Vue will still add
        // the listener, so we end up triggering both
        onClick: n.navigate,
        class: s.value
      }, o);
    };
  }
}), Li = ji;
function Fi(e) {
  if (!(e.metaKey || e.altKey || e.ctrlKey || e.shiftKey) && !e.defaultPrevented && !(e.button !== void 0 && e.button !== 0)) {
    if (e.currentTarget && e.currentTarget.getAttribute) {
      const t = e.currentTarget.getAttribute("target");
      if (/\b_blank\b/i.test(t))
        return;
    }
    return e.preventDefault && e.preventDefault(), !0;
  }
}
function Ui(e, t) {
  for (const n in t) {
    const r = t[n], s = e[n];
    if (typeof r == "string") {
      if (r !== s)
        return !1;
    } else if (!ee(s) || s.length !== r.length || r.some((o, i) => o !== s[i]))
      return !1;
  }
  return !0;
}
function hn(e) {
  return e ? e.aliasOf ? e.aliasOf.path : e.path : "";
}
const pn = (e, t, n) => e ?? t ?? n, Wi = /* @__PURE__ */ X({
  name: "RouterView",
  // #674 we manually inherit them
  inheritAttrs: !1,
  props: {
    name: {
      type: String,
      default: "default"
    },
    route: Object
  },
  // Better compat for @vue/compat users
  // https://github.com/vuejs/router/issues/1315
  compatConfig: { MODE: 3 },
  setup(e, { attrs: t, slots: n }) {
    O.NODE_ENV !== "production" && Hi();
    const r = le(Pt), s = B(() => e.route || r.value), o = le(fn, 0), i = B(() => {
      let d = Q(o);
      const { matched: u } = s.value;
      let l;
      for (; (l = u[d]) && !l.components; )
        d++;
      return d;
    }), a = B(() => s.value.matched[i.value]);
    H(fn, B(() => i.value + 1)), H(Di, a), H(Pt, s);
    const c = L();
    return G(() => [c.value, a.value, e.name], ([d, u, l], [f, h, p]) => {
      u && (u.instances[l] = d, h && h !== u && d && d === f && (u.leaveGuards.size || (u.leaveGuards = h.leaveGuards), u.updateGuards.size || (u.updateGuards = h.updateGuards))), d && u && // if there is no instance but to and from are the same this might be
      // the first visit
      (!h || !pe(u, h) || !f) && (u.enterCallbacks[l] || []).forEach((m) => m(d));
    }, { flush: "post" }), () => {
      const d = s.value, u = e.name, l = a.value, f = l && l.components[u];
      if (!f)
        return mn(n.default, { Component: f, route: d });
      const h = l.props[u], p = h ? h === !0 ? d.params : typeof h == "function" ? h(d) : h : null, y = q(f, x({}, p, t, {
        onVnodeUnmounted: (w) => {
          w.component.isUnmounted && (l.instances[u] = null);
        },
        ref: c
      }));
      if (O.NODE_ENV !== "production" && ie && y.ref) {
        const w = {
          depth: i.value,
          name: l.name,
          path: l.path,
          meta: l.meta
        };
        (ee(y.ref) ? y.ref.map((k) => k.i) : [y.ref.i]).forEach((k) => {
          k.__vrv_devtools = w;
        });
      }
      return (
        // pass the vnode to the slot as a prop.
        // h and <component :is="..."> both accept vnodes
        mn(n.default, { Component: y, route: d }) || y
      );
    };
  }
});
function mn(e, t) {
  if (!e)
    return null;
  const n = e(t);
  return n.length === 1 ? n[0] : n;
}
const zi = Wi;
function Hi() {
  const e = Ge(), t = e.parent && e.parent.type.name, n = e.parent && e.parent.subTree && e.parent.subTree.type;
  if (t && (t === "KeepAlive" || t.includes("Transition")) && typeof n == "object" && n.name === "RouterView") {
    const r = t === "KeepAlive" ? "keep-alive" : "transition";
    P(`<router-view> can no longer be used directly inside <transition> or <keep-alive>.
Use slot props instead:

<router-view v-slot="{ Component }">
  <${r}>
    <component :is="Component" />
  </${r}>
</router-view>`);
  }
}
function Ae(e, t) {
  const n = x({}, e, {
    // remove variables that can contain vue instances
    matched: e.matched.map((r) => na(r, ["instances", "children", "aliasOf"]))
  });
  return {
    _custom: {
      type: null,
      readOnly: !0,
      display: e.fullPath,
      tooltip: t,
      value: n
    }
  };
}
function Ue(e) {
  return {
    _custom: {
      display: e
    }
  };
}
let Ki = 0;
function Gi(e, t, n) {
  if (t.__hasDevtools)
    return;
  t.__hasDevtools = !0;
  const r = Ki++;
  Bo({
    id: "org.vuejs.router" + (r ? "." + r : ""),
    label: "Vue Router",
    packageName: "vue-router",
    homepage: "https://router.vuejs.org",
    logo: "https://router.vuejs.org/logo.png",
    componentStateTypes: ["Routing"],
    app: e
  }, (s) => {
    typeof s.now != "function" && console.warn("[Vue Router]: You seem to be using an outdated version of Vue Devtools. Are you still using the Beta release instead of the stable one? You can find the links at https://devtools.vuejs.org/guide/installation.html."), s.on.inspectComponent((u, l) => {
      u.instanceData && u.instanceData.state.push({
        type: "Routing",
        key: "$route",
        editable: !1,
        value: Ae(t.currentRoute.value, "Current Route")
      });
    }), s.on.visitComponentTree(({ treeNode: u, componentInstance: l }) => {
      if (l.__vrv_devtools) {
        const f = l.__vrv_devtools;
        u.tags.push({
          label: (f.name ? `${f.name.toString()}: ` : "") + f.path,
          textColor: 0,
          tooltip: "This component is rendered by &lt;router-view&gt;",
          backgroundColor: Er
        });
      }
      ee(l.__vrl_devtools) && (l.__devtoolsApi = s, l.__vrl_devtools.forEach((f) => {
        let h = f.route.path, p = kr, m = "", y = 0;
        f.error ? (h = f.error, p = Xi, y = Zi) : f.isExactActive ? (p = Sr, m = "This is exactly active") : f.isActive && (p = br, m = "This link is active"), u.tags.push({
          label: h,
          textColor: y,
          tooltip: m,
          backgroundColor: p
        });
      }));
    }), G(t.currentRoute, () => {
      c(), s.notifyComponentUpdate(), s.sendInspectorTree(a), s.sendInspectorState(a);
    });
    const o = "router:navigations:" + r;
    s.addTimelineLayer({
      id: o,
      label: `Router${r ? " " + r : ""} Navigations`,
      color: 4237508
    }), t.onError((u, l) => {
      s.addTimelineEvent({
        layerId: o,
        event: {
          title: "Error during Navigation",
          subtitle: l.fullPath,
          logType: "error",
          time: s.now(),
          data: { error: u },
          groupId: l.meta.__navigationId
        }
      });
    });
    let i = 0;
    t.beforeEach((u, l) => {
      const f = {
        guard: Ue("beforeEach"),
        from: Ae(l, "Current Location during this navigation"),
        to: Ae(u, "Target location")
      };
      Object.defineProperty(u.meta, "__navigationId", {
        value: i++
      }), s.addTimelineEvent({
        layerId: o,
        event: {
          time: s.now(),
          title: "Start of navigation",
          subtitle: u.fullPath,
          data: f,
          groupId: u.meta.__navigationId
        }
      });
    }), t.afterEach((u, l, f) => {
      const h = {
        guard: Ue("afterEach")
      };
      f ? (h.failure = {
        _custom: {
          type: Error,
          readOnly: !0,
          display: f ? f.message : "",
          tooltip: "Navigation Failure",
          value: f
        }
      }, h.status = Ue("❌")) : h.status = Ue("✅"), h.from = Ae(l, "Current Location during this navigation"), h.to = Ae(u, "Target location"), s.addTimelineEvent({
        layerId: o,
        event: {
          title: "End of navigation",
          subtitle: u.fullPath,
          time: s.now(),
          data: h,
          logType: f ? "warning" : "default",
          groupId: u.meta.__navigationId
        }
      });
    });
    const a = "router-inspector:" + r;
    s.addInspector({
      id: a,
      label: "Routes" + (r ? " " + r : ""),
      icon: "book",
      treeFilterPlaceholder: "Search routes"
    });
    function c() {
      if (!d)
        return;
      const u = d;
      let l = n.getRoutes().filter((f) => !f.parent || // these routes have a parent with no component which will not appear in the view
      // therefore we still need to include them
      !f.parent.record.components);
      l.forEach(Pr), u.filter && (l = l.filter((f) => (
        // save matches state based on the payload
        Nt(f, u.filter.toLowerCase())
      ))), l.forEach((f) => Or(f, t.currentRoute.value)), u.rootNodes = l.map(Rr);
    }
    let d;
    s.on.getInspectorTree((u) => {
      d = u, u.app === e && u.inspectorId === a && c();
    }), s.on.getInspectorState((u) => {
      if (u.app === e && u.inspectorId === a) {
        const f = n.getRoutes().find((h) => h.record.__vd_id === u.nodeId);
        f && (u.state = {
          options: Ji(f)
        });
      }
    }), s.sendInspectorTree(a), s.sendInspectorState(a);
  });
}
function qi(e) {
  return e.optional ? e.repeatable ? "*" : "?" : e.repeatable ? "+" : "";
}
function Ji(e) {
  const { record: t } = e, n = [
    { editable: !1, key: "path", value: t.path }
  ];
  return t.name != null && n.push({
    editable: !1,
    key: "name",
    value: t.name
  }), n.push({ editable: !1, key: "regexp", value: e.re }), e.keys.length && n.push({
    editable: !1,
    key: "keys",
    value: {
      _custom: {
        type: null,
        readOnly: !0,
        display: e.keys.map((r) => `${r.name}${qi(r)}`).join(" "),
        tooltip: "Param keys",
        value: e.keys
      }
    }
  }), t.redirect != null && n.push({
    editable: !1,
    key: "redirect",
    value: t.redirect
  }), e.alias.length && n.push({
    editable: !1,
    key: "aliases",
    value: e.alias.map((r) => r.record.path)
  }), Object.keys(e.record.meta).length && n.push({
    editable: !1,
    key: "meta",
    value: e.record.meta
  }), n.push({
    key: "score",
    editable: !1,
    value: {
      _custom: {
        type: null,
        readOnly: !0,
        display: e.score.map((r) => r.join(", ")).join(" | "),
        tooltip: "Score used to sort routes",
        value: e.score
      }
    }
  }), n;
}
const Er = 15485081, br = 2450411, Sr = 8702998, Qi = 2282478, kr = 16486972, Yi = 6710886, Xi = 16704226, Zi = 12131356;
function Rr(e) {
  const t = [], { record: n } = e;
  n.name != null && t.push({
    label: String(n.name),
    textColor: 0,
    backgroundColor: Qi
  }), n.aliasOf && t.push({
    label: "alias",
    textColor: 0,
    backgroundColor: kr
  }), e.__vd_match && t.push({
    label: "matches",
    textColor: 0,
    backgroundColor: Er
  }), e.__vd_exactActive && t.push({
    label: "exact",
    textColor: 0,
    backgroundColor: Sr
  }), e.__vd_active && t.push({
    label: "active",
    textColor: 0,
    backgroundColor: br
  }), n.redirect && t.push({
    label: typeof n.redirect == "string" ? `redirect: ${n.redirect}` : "redirects",
    textColor: 16777215,
    backgroundColor: Yi
  });
  let r = n.__vd_id;
  return r == null && (r = String(ea++), n.__vd_id = r), {
    id: r,
    label: n.path,
    tags: t,
    children: e.children.map(Rr)
  };
}
let ea = 0;
const ta = /^\/(.*)\/([a-z]*)$/;
function Or(e, t) {
  const n = t.matched.length && pe(t.matched[t.matched.length - 1], e.record);
  e.__vd_exactActive = e.__vd_active = n, n || (e.__vd_active = t.matched.some((r) => pe(r, e.record))), e.children.forEach((r) => Or(r, t));
}
function Pr(e) {
  e.__vd_match = !1, e.children.forEach(Pr);
}
function Nt(e, t) {
  const n = String(e.re).match(ta);
  if (e.__vd_match = !1, !n || n.length < 3)
    return !1;
  if (new RegExp(n[1].replace(/\$$/, ""), n[2]).test(t))
    return e.children.forEach((i) => Nt(i, t)), e.record.path !== "/" || t === "/" ? (e.__vd_match = e.re.test(t), !0) : !1;
  const s = e.record.path.toLowerCase(), o = Pe(s);
  return !t.startsWith("/") && (o.includes(t) || s.includes(t)) || o.startsWith(t) || s.startsWith(t) || e.record.name && String(e.record.name).includes(t) ? !0 : e.children.some((i) => Nt(i, t));
}
function na(e, t) {
  const n = {};
  for (const r in e)
    t.includes(r) || (n[r] = e[r]);
  return n;
}
function ra(e) {
  const t = Ri(e.routes, e), n = e.parseQuery || Ti, r = e.stringifyQuery || un, s = e.history;
  if (O.NODE_ENV !== "production" && !s)
    throw new Error('Provide the "history" option when calling "createRouter()": https://router.vuejs.org/api/interfaces/RouterOptions.html#history');
  const o = Ce(), i = Ce(), a = Ce(), c = ce(ue);
  let d = ue;
  ie && e.scrollBehavior && "scrollRestoration" in history && (history.scrollRestoration = "manual");
  const u = at.bind(null, (g) => "" + g), l = at.bind(null, Xo), f = (
    // @ts-expect-error: intentionally avoid the type check
    at.bind(null, Pe)
  );
  function h(g, b) {
    let E, S;
    return vr(g) ? (E = t.getRecordMatcher(g), O.NODE_ENV !== "production" && !E && P(`Parent route "${String(g)}" not found when adding child route`, b), S = b) : S = g, t.addRoute(S, E);
  }
  function p(g) {
    const b = t.getRecordMatcher(g);
    b ? t.removeRoute(b) : O.NODE_ENV !== "production" && P(`Cannot remove non-existent route "${String(g)}"`);
  }
  function m() {
    return t.getRoutes().map((g) => g.record);
  }
  function y(g) {
    return !!t.getRecordMatcher(g);
  }
  function w(g, b) {
    if (b = x({}, b || c.value), typeof g == "string") {
      const V = ct(n, g, b.path), F = t.resolve({ path: V.path }, b), me = s.createHref(V.fullPath);
      return O.NODE_ENV !== "production" && (me.startsWith("//") ? P(`Location "${g}" resolved to "${me}". A resolved location cannot start with multiple slashes.`) : F.matched.length || P(`No match found for location with path "${g}"`)), x(V, F, {
        params: f(F.params),
        hash: Pe(V.hash),
        redirectedFrom: void 0,
        href: me
      });
    }
    if (O.NODE_ENV !== "production" && !Ke(g))
      return P(`router.resolve() was passed an invalid location. This will fail in production.
- Location:`, g), w({});
    let E;
    if (g.path != null)
      O.NODE_ENV !== "production" && "params" in g && !("name" in g) && // @ts-expect-error: the type is never
      Object.keys(g.params).length && P(`Path "${g.path}" was passed with params but they will be ignored. Use a named route alongside params instead.`), E = x({}, g, {
        path: ct(n, g.path, b.path).path
      });
    else {
      const V = x({}, g.params);
      for (const F in V)
        V[F] == null && delete V[F];
      E = x({}, g, {
        params: l(V)
      }), b.params = l(b.params);
    }
    const S = t.resolve(E, b), $ = g.hash || "";
    O.NODE_ENV !== "production" && $ && !$.startsWith("#") && P(`A \`hash\` should always start with the character "#". Replace "${$}" with "#${$}".`), S.params = u(f(S.params));
    const z = ti(r, x({}, g, {
      hash: Jo($),
      path: S.path
    })), C = s.createHref(z);
    return O.NODE_ENV !== "production" && (C.startsWith("//") ? P(`Location "${g}" resolved to "${C}". A resolved location cannot start with multiple slashes.`) : S.matched.length || P(`No match found for location with path "${g.path != null ? g.path : g}"`)), x({
      fullPath: z,
      // keep the hash encoded so fullPath is effectively path + encodedQuery +
      // hash
      hash: $,
      query: (
        // if the user is using a custom query lib like qs, we might have
        // nested objects, so we keep the query as is, meaning it can contain
        // numbers at `$route.query`, but at the point, the user will have to
        // use their own type anyway.
        // https://github.com/vuejs/router/issues/328#issuecomment-649481567
        r === un ? Ii(g.query) : g.query || {}
      )
    }, S, {
      redirectedFrom: void 0,
      href: C
    });
  }
  function _(g) {
    return typeof g == "string" ? ct(n, g, c.value.path) : x({}, g);
  }
  function k(g, b) {
    if (d !== g)
      return Ve(8, {
        from: b,
        to: g
      });
  }
  function v(g) {
    return I(g);
  }
  function R(g) {
    return v(x(_(g), { replace: !0 }));
  }
  function A(g) {
    const b = g.matched[g.matched.length - 1];
    if (b && b.redirect) {
      const { redirect: E } = b;
      let S = typeof E == "function" ? E(g) : E;
      if (typeof S == "string" && (S = S.includes("?") || S.includes("#") ? S = _(S) : (
        // force empty params
        { path: S }
      ), S.params = {}), O.NODE_ENV !== "production" && S.path == null && !("name" in S))
        throw P(`Invalid redirect found:
${JSON.stringify(S, null, 2)}
 when navigating to "${g.fullPath}". A redirect must contain a name or path. This will break in production.`), new Error("Invalid redirect");
      return x({
        query: g.query,
        hash: g.hash,
        // avoid transferring params if the redirect has a path
        params: S.path != null ? {} : g.params
      }, S);
    }
  }
  function I(g, b) {
    const E = d = w(g), S = c.value, $ = g.state, z = g.force, C = g.replace === !0, V = A(E);
    if (V)
      return I(
        x(_(V), {
          state: typeof V == "object" ? x({}, $, V.state) : $,
          force: z,
          replace: C
        }),
        // keep original redirectedFrom if it exists
        b || E
      );
    const F = E;
    F.redirectedFrom = b;
    let me;
    return !z && Xt(r, S, E) && (me = Ve(16, { to: F, from: S }), Lt(
      S,
      S,
      // this is a push, the only way for it to be triggered from a
      // history.listen is with a redirect, which makes it become a push
      !0,
      // This cannot be the first navigation because the initial location
      // cannot be manually navigated to
      !1
    )), (me ? Promise.resolve(me) : N(F, S)).catch((J) => oe(J) ? (
      // navigation redirects still mark the router as ready
      oe(
        J,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? J : st(J)
    ) : (
      // reject any unknown error
      rt(J, F, S)
    )).then((J) => {
      if (J) {
        if (oe(
          J,
          2
          /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
        ))
          return O.NODE_ENV !== "production" && // we are redirecting to the same location we were already at
          Xt(r, w(J.to), F) && // and we have done it a couple of times
          b && // @ts-expect-error: added only in dev
          (b._count = b._count ? (
            // @ts-expect-error
            b._count + 1
          ) : 1) > 30 ? (P(`Detected a possibly infinite redirection in a navigation guard when going from "${S.fullPath}" to "${F.fullPath}". Aborting to avoid a Stack Overflow.
 Are you always returning a new location within a navigation guard? That would lead to this error. Only return when redirecting or aborting, that should fix this. This might break in production if not fixed.`), Promise.reject(new Error("Infinite redirect in navigation guard"))) : I(
            // keep options
            x({
              // preserve an existing replacement but allow the redirect to override it
              replace: C
            }, _(J.to), {
              state: typeof J.to == "object" ? x({}, $, J.to.state) : $,
              force: z
            }),
            // preserve the original redirectedFrom if any
            b || F
          );
      } else
        J = W(F, S, !0, C, $);
      return M(F, S, J), J;
    });
  }
  function U(g, b) {
    const E = k(g, b);
    return E ? Promise.reject(E) : Promise.resolve();
  }
  function Z(g) {
    const b = je.values().next().value;
    return b && typeof b.runWithContext == "function" ? b.runWithContext(g) : g();
  }
  function N(g, b) {
    let E;
    const [S, $, z] = sa(g, b);
    E = ut(S.reverse(), "beforeRouteLeave", g, b);
    for (const V of S)
      V.leaveGuards.forEach((F) => {
        E.push(fe(F, g, b));
      });
    const C = U.bind(null, g, b);
    return E.push(C), _e(E).then(() => {
      E = [];
      for (const V of o.list())
        E.push(fe(V, g, b));
      return E.push(C), _e(E);
    }).then(() => {
      E = ut($, "beforeRouteUpdate", g, b);
      for (const V of $)
        V.updateGuards.forEach((F) => {
          E.push(fe(F, g, b));
        });
      return E.push(C), _e(E);
    }).then(() => {
      E = [];
      for (const V of z)
        if (V.beforeEnter)
          if (ee(V.beforeEnter))
            for (const F of V.beforeEnter)
              E.push(fe(F, g, b));
          else
            E.push(fe(V.beforeEnter, g, b));
      return E.push(C), _e(E);
    }).then(() => (g.matched.forEach((V) => V.enterCallbacks = {}), E = ut(z, "beforeRouteEnter", g, b, Z), E.push(C), _e(E))).then(() => {
      E = [];
      for (const V of i.list())
        E.push(fe(V, g, b));
      return E.push(C), _e(E);
    }).catch((V) => oe(
      V,
      8
      /* ErrorTypes.NAVIGATION_CANCELLED */
    ) ? V : Promise.reject(V));
  }
  function M(g, b, E) {
    a.list().forEach((S) => Z(() => S(g, b, E)));
  }
  function W(g, b, E, S, $) {
    const z = k(g, b);
    if (z)
      return z;
    const C = b === ue, V = ie ? history.state : {};
    E && (S || C ? s.replace(g.fullPath, x({
      scroll: C && V && V.scroll
    }, $)) : s.push(g.fullPath, $)), c.value = g, Lt(g, b, E, C), st();
  }
  let te;
  function $r() {
    te || (te = s.listen((g, b, E) => {
      if (!Ft.listening)
        return;
      const S = w(g), $ = A(S);
      if ($) {
        I(x($, { replace: !0, force: !0 }), S).catch(xe);
        return;
      }
      d = S;
      const z = c.value;
      ie && ai(en(z.fullPath, E.delta), Qe()), N(S, z).catch((C) => oe(
        C,
        12
        /* ErrorTypes.NAVIGATION_CANCELLED */
      ) ? C : oe(
        C,
        2
        /* ErrorTypes.NAVIGATION_GUARD_REDIRECT */
      ) ? (I(
        x(_(C.to), {
          force: !0
        }),
        S
        // avoid an uncaught rejection, let push call triggerError
      ).then((V) => {
        oe(
          V,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && !E.delta && E.type === Ne.pop && s.go(-1, !1);
      }).catch(xe), Promise.reject()) : (E.delta && s.go(-E.delta, !1), rt(C, S, z))).then((C) => {
        C = C || W(
          // after navigation, all matched components are resolved
          S,
          z,
          !1
        ), C && (E.delta && // a new navigation has been triggered, so we do not want to revert, that will change the current history
        // entry while a different route is displayed
        !oe(
          C,
          8
          /* ErrorTypes.NAVIGATION_CANCELLED */
        ) ? s.go(-E.delta, !1) : E.type === Ne.pop && oe(
          C,
          20
          /* ErrorTypes.NAVIGATION_DUPLICATED */
        ) && s.go(-1, !1)), M(S, z, C);
      }).catch(xe);
    }));
  }
  let nt = Ce(), jt = Ce(), Be;
  function rt(g, b, E) {
    st(g);
    const S = jt.list();
    return S.length ? S.forEach(($) => $(g, b, E)) : (O.NODE_ENV !== "production" && P("uncaught error during route navigation:"), console.error(g)), Promise.reject(g);
  }
  function Tr() {
    return Be && c.value !== ue ? Promise.resolve() : new Promise((g, b) => {
      nt.add([g, b]);
    });
  }
  function st(g) {
    return Be || (Be = !g, $r(), nt.list().forEach(([b, E]) => g ? E(g) : b()), nt.reset()), g;
  }
  function Lt(g, b, E, S) {
    const { scrollBehavior: $ } = e;
    if (!ie || !$)
      return Promise.resolve();
    const z = !E && ci(en(g.fullPath, 0)) || (S || !E) && history.state && history.state.scroll || null;
    return ke().then(() => $(g, b, z)).then((C) => C && ii(C)).catch((C) => rt(C, g, b));
  }
  const ot = (g) => s.go(g);
  let it;
  const je = /* @__PURE__ */ new Set(), Ft = {
    currentRoute: c,
    listening: !0,
    addRoute: h,
    removeRoute: p,
    clearRoutes: t.clearRoutes,
    hasRoute: y,
    getRoutes: m,
    resolve: w,
    options: e,
    push: v,
    replace: R,
    go: ot,
    back: () => ot(-1),
    forward: () => ot(1),
    beforeEach: o.add,
    beforeResolve: i.add,
    afterEach: a.add,
    onError: jt.add,
    isReady: Tr,
    install(g) {
      const b = this;
      g.component("RouterLink", Li), g.component("RouterView", zi), g.config.globalProperties.$router = b, Object.defineProperty(g.config.globalProperties, "$route", {
        enumerable: !0,
        get: () => Q(c)
      }), ie && // used for the initial navigation client side to avoid pushing
      // multiple times when the router is used in multiple apps
      !it && c.value === ue && (it = !0, v(s.location).catch(($) => {
        O.NODE_ENV !== "production" && P("Unexpected error when starting the router:", $);
      }));
      const E = {};
      for (const $ in ue)
        Object.defineProperty(E, $, {
          get: () => c.value[$],
          enumerable: !0
        });
      g.provide(Ye, b), g.provide(Bt, Hr(E)), g.provide(Pt, c);
      const S = g.unmount;
      je.add(g), g.unmount = function() {
        je.delete(g), je.size < 1 && (d = ue, te && te(), te = null, c.value = ue, it = !1, Be = !1), S();
      }, O.NODE_ENV !== "production" && ie && Gi(g, b, t);
    }
  };
  function _e(g) {
    return g.reduce((b, E) => b.then(() => Z(E)), Promise.resolve());
  }
  return Ft;
}
function sa(e, t) {
  const n = [], r = [], s = [], o = Math.max(t.matched.length, e.matched.length);
  for (let i = 0; i < o; i++) {
    const a = t.matched[i];
    a && (e.matched.find((d) => pe(d, a)) ? r.push(a) : n.push(a));
    const c = e.matched[i];
    c && (t.matched.find((d) => pe(d, c)) || s.push(c));
  }
  return [n, r, s];
}
function oa() {
  return le(Ye);
}
function ia(e) {
  return le(Bt);
}
const Nr = Symbol("BINDING_GETTER_KEY");
function aa(e, t) {
  const n = fa(e, t);
  return ca(e, n, t), Gr(() => {
    n._release();
  }), H(Nr, n), {
    bindingGetter: n
  };
}
function ca(e, t, n) {
  var s, o, i, a, c, d, u;
  const { id: r } = e;
  if (la(n.vforSetting, r, t), ua(n.slotSetting, r, t), e.routerParam) {
    const l = D(r, e.routerParam), f = ia(), h = B(() => f.params);
    t._registerBinding(l, h), H(l, h);
  }
  if (e.routerAct) {
    const l = D(r, e.routerAct), f = oa();
    t._registerBinding(l, f), H(l, f);
  }
  (s = e.data) == null || s.forEach((l) => {
    const f = D(r, l.id);
    t._registerBinding(f, l.value), H(f, l.value);
  }), (o = e.jsFn) == null || o.forEach((l) => {
    const f = D(r, l.id), h = da(l);
    t._registerBinding(f, h), H(f, h);
  }), (i = e.eRefs) == null || i.forEach((l) => {
    const f = D(r, l.id), h = ce(null);
    t._registerBinding(f, h), H(f, h);
  }), (a = e.refs) == null || a.forEach((l) => {
    const { id: f, constData: h } = l, m = h !== void 0 ? t.getValue(l.value) : l.value, y = D(r, f), w = yo({ ...l, value: m });
    t._registerBinding(y, w), H(y, w);
  }), (c = e.web_computed) == null || c.forEach((l) => {
    const f = D(r, l.id), h = wo(l);
    t._registerBinding(f, h), H(f, h);
  }), bo(e).forEach((l) => {
    if (l.type === "js") {
      const p = D(r, l.item.id), m = _o(
        l.item,
        t
      );
      t._registerBinding(p, m), H(p, m);
      return;
    }
    const f = D(r, l.item.id), h = vo(
      l.item,
      t
    );
    t._registerBinding(f, h), H(f, h);
  }), ko({
    watchConfigs: e.py_watch || [],
    computedConfigs: e.web_computed || [],
    bindingGetter: t,
    sid: r
  }), (d = e.js_watch) == null || d.forEach((l) => {
    Co(l, t);
  }), (u = e.vue_watch) == null || u.forEach((l) => {
    Vo(l, t);
  });
}
function la(e, t, n) {
  if (e != null && e.item) {
    const { id: r } = e.item, s = D(t, r), o = ha(e.item, n);
    n._registerBinding(s, o), H(s, o);
  }
  if (e != null && e.index) {
    const { id: r, value: s } = e.index, o = D(t, r), i = L(s);
    n._registerBinding(o, i), H(o, i);
  }
  if (e != null && e.key) {
    const { id: r, value: s } = e.key, o = D(t, r), i = L(s);
    n._registerBinding(o, i), H(o, i);
  }
}
function ua(e, t, n) {
  if (!e)
    return;
  const { id: r, value: s } = e, o = D(t, r), i = ce(s);
  n._registerBinding(o, i), H(o, i);
}
function fa(e, t) {
  const { binds: n } = e, r = /* @__PURE__ */ new Map(), s = /* @__PURE__ */ new Map();
  let o = null, i = null;
  const a = pa(
    n,
    e.web_computed,
    e.id,
    t
  );
  a == null || a.forEach((v, R) => {
    const { sid: A, id: I } = v, U = D(A, I);
    if (A !== e.id) {
      const Z = le(U);
      r.set(R, Z);
    } else
      s.set(U, R);
  });
  function c(v) {
    const R = d(v);
    return Ps(R, {
      paths: v.path,
      getBindableValueFn: u
    });
  }
  function d(v) {
    const R = r.get(v.r);
    if (!R)
      throw new Error(`Binding not found: ${JSON.stringify(v)}`);
    return R;
  }
  function u(v) {
    return Se(c(v));
  }
  function l(v) {
    const R = r.get(v.r);
    if (!R)
      throw new Error(`Router binding not found: ${JSON.stringify(v)}`);
    return R;
  }
  function f(v, R) {
    if (Qn(v)) {
      const A = d(v);
      if (v.path) {
        Hn(A.value, v.path, R, u);
        return;
      }
      A.value = R;
      return;
    }
    throw new Error(`Unsupported output binding: ${v}`);
  }
  function h(v) {
    if (v != null && v.item) {
      const { id: R, value: A, sourceInfo: I } = v.item;
      if (I) {
        const { index: N, key: M } = I;
        o && (o.value = N), i && (i.value = M);
      }
      const U = D(e.id, R), Z = c({ r: m(U) });
      Z.value = A;
    }
    if (v != null && v.index) {
      const { id: R, value: A } = v.index, I = D(e.id, R), U = c({ r: m(I) });
      U.value = A;
    }
    if (v != null && v.key) {
      const { id: R, value: A } = v.key, I = D(e.id, R), U = c({ r: m(I) });
      U.value = A;
    }
  }
  function p(v) {
    if (!v)
      return;
    const { id: R, value: A } = v, I = D(e.id, R), U = c({ r: m(I) });
    U.value = A;
  }
  function m(v) {
    return s.get(v);
  }
  function y(v, R) {
    const A = s.get(v);
    A !== void 0 && r.set(A, R);
  }
  function w() {
    r.clear(), s.clear();
  }
  function _(v) {
    return o = L(v), o;
  }
  function k(v) {
    return i = L(v), i;
  }
  return {
    getValue: u,
    getRef: c,
    updateValue: f,
    getBindIndex: m,
    updateVForInfo: h,
    updateSlotInfo: p,
    getRouter: l,
    initVForIndexRef: _,
    initVForKeyRef: k,
    _registerBinding: y,
    _release: w
  };
}
function D(e, t) {
  return `${e}-${t}`;
}
function da(e) {
  const { immediately: t = !1, code: n } = e;
  let r = Y(n);
  return t && (r = r()), de(() => ({
    get() {
      return r;
    },
    set() {
      throw new Error("Cannot set value to js function");
    }
  }));
}
function Nc() {
  const { getRef: e, getRouter: t, getValue: n } = le(Nr);
  return {
    getRef: e,
    getRouter: t,
    getValue: n
  };
}
function ha(e, t) {
  const { value: n, sourceInfo: r } = e;
  if (r) {
    const { source: s, type: o, index: i, key: a } = r, c = t.initVForIndexRef(i);
    return o === "array" ? de(() => ({
      get() {
        return s.value[c.value];
      },
      set(d) {
        s.value[c.value] = d;
      }
    })) : de(() => {
      const d = t.initVForKeyRef(a);
      return {
        get() {
          return s.value[d.value];
        },
        set(u) {
          s.value[d.value] = u;
        }
      };
    });
  }
  return L(n);
}
function pa(e, t, n, r) {
  const s = new Set(e == null ? void 0 : e.map((c) => D(c.sid, c.id))), o = ma(
    e,
    s,
    t,
    n
  ), i = ga(
    o,
    s,
    n,
    r
  );
  return ya(
    i,
    s,
    n,
    r
  );
}
function ma(e, t, n, r) {
  if (!n)
    return e;
  const s = n.filter((o) => !t.has(D(r, o.id))).map((o) => ({ id: o.id, sid: r }));
  return [...e ?? [], ...s];
}
function ga(e, t, n, r) {
  if (!r.vforSetting)
    return e;
  const s = [];
  return r.vforSetting.item && !t.has(D(n, r.vforSetting.item.id)) && s.push({
    id: r.vforSetting.item.id,
    sid: n
  }), r.vforSetting.index && !t.has(D(n, r.vforSetting.index.id)) && s.push({
    id: r.vforSetting.index.id,
    sid: n
  }), r.vforSetting.key && !t.has(D(n, r.vforSetting.key.id)) && s.push({
    id: r.vforSetting.key.id,
    sid: n
  }), [...e ?? [], ...s];
}
function ya(e, t, n, r) {
  return !r.slotSetting || t.has(D(n, r.slotSetting.id)) ? e : [
    ...e ?? [],
    { id: r.slotSetting.id, sid: n }
  ];
}
const Vr = "__INSTAUI_UNWRAP_KEY__";
function va(e, t) {
  const n = wa(e, t), r = kn(n), s = xn(e, t), { styles: o, hasStyle: i } = $n(e, t), a = Dn(e, t), c = Rn(a) || {};
  i && (c.style = o), s && (c.class = s);
  const { slotUnwrap: d } = e, u = new Set(d || []), l = Object.fromEntries(
    Object.entries(e.slots || {}).map(([h, p]) => u.has(h) ? [mt(h), _a(p, t)] : [mt(h), In(t)(p)])
  );
  let f = q(r, { ...c }, l);
  return f = Un(f, e.events, t), f = Wn(f, e, t), Tn(f, e, t);
}
function wa(e, t) {
  const { tag: n } = e;
  return typeof n == "string" ? n : t.bindingGetter.getValue(n);
}
function _a(e, t) {
  return () => {
    var o, i;
    const n = e.items;
    if (n.length === 0)
      return null;
    const r = n[0];
    if (r.type === "logic" && r.tag === "vfor") {
      const a = r, { fkey: c } = a, { sourceInfo: d, iterSource: u } = qn(a, t), l = [];
      for (const [f, h, p] of u)
        (i = (o = a.scope) == null ? void 0 : o.items) == null || i.forEach((m) => {
          const y = ba(a, d), w = vt(
            m,
            Ea(t, {
              value: { index: f, key: p, item: h },
              vforComponent: a
            }),
            y,
            {
              [Vr]: {
                value: {
                  index: f,
                  key: p,
                  item: h
                }
              }
            }
          ), _ = Jn(c, { value: h, index: f }), k = re(w, { key: _ });
          l.push(k);
        });
      return l;
    }
    return e.items.map((a) => vt(a, t));
  };
}
function Ea(e, t) {
  const { getValue: n } = e.bindingGetter, { vforComponent: r } = t, { scope: s, used: o } = r;
  if (!s || !o)
    return e;
  const { id: i, binds: a } = s;
  if (!a)
    return e;
  const c = /* @__PURE__ */ new Map(), { index: d, key: u, item: l } = o;
  d && c.set(d, t.value.index), u && c.set(u, t.value.key), l && c.set(l, t.value.item);
  const f = new Map(
    a.map((p, m) => ({ index: m, bind: p })).filter((p) => p.bind.sid === i).map((p) => {
      const { id: m } = p.bind;
      return [p.index, c.get(m)];
    })
  ), h = (p) => {
    const { r: m } = p;
    return f.has(m) ? f.get(m) : n(p);
  };
  return {
    ...e,
    bindingGetter: {
      ...e.bindingGetter,
      getValue: h
    }
  };
}
function ba(e, t) {
  return () => {
    const { scope: n, used: r } = e;
    if (!n || !r)
      return;
    const { id: s } = n, o = /* @__PURE__ */ new Map(), { index: i, key: a, item: c } = r, d = Pn(), u = B(
      () => d[Vr]
    );
    if (i) {
      const l = L(u.value.value.index);
      H(D(s, i), l), o.set(i, l);
    }
    if (a) {
      const l = L(u.value.value.key);
      H(D(s, a), l), o.set(a, l);
    }
    if (c) {
      const l = de((f, h) => ({
        get() {
          return f(), u.value.value.item;
        },
        set(p) {
          t && (t.source.value[u.value.value.index] = p, h());
        }
      }));
      H(D(s, c), l), o.set(c, l);
    }
    G(u, (l) => {
      const { index: f, key: h, item: p } = l.value;
      i && (o.get(i).value = f), a && (o.get(a).value = h), c && (o.get(c).value = p);
    });
  };
}
function Sa(e, t) {
  const { on: n, items: r } = e;
  return (typeof n == "boolean" ? n : t.bindingGetter.getValue(n)) ? r == null ? void 0 : r.map((o) => we(o, t)) : void 0;
}
function ka(e, t) {
  const { cond: n, const: r = 0, cases: s, default: o } = e, a = r === 1 ? n : t.bindingGetter.getValue(n), c = [];
  let d = !1;
  for (const { value: u, items: l = [] } of s || [])
    if (u === a) {
      c.push(...l.map((f) => we(f, t))), d = !0;
      break;
    }
  return !d && o && o.items && c.push(
    ...o.items.map((u) => we(u, t))
  ), c;
}
function Ra(e, t) {
  const { value: n, r = 0 } = e, s = r === 1 ? t.bindingGetter.getValue(n) : n;
  return qr(s);
}
const Oa = /* @__PURE__ */ new Map(
  [
    ["vfor", Cs],
    ["vif", Sa],
    ["match", ka],
    ["content", Ra]
  ]
);
function Pa(e, t) {
  const n = Oa.get(e.tag);
  if (!n)
    throw new Error(`Unknown logic component ${e.tag}`);
  return n(e, t);
}
function we(e, t) {
  const { type: n } = e;
  if (n === "cp")
    return vt(e, t);
  if (n === "logic")
    return Pa(e, t);
  if (n === "scope")
    return Me(e, {
      buildOptions: t
    });
  if (n === "scp")
    return va(e, t);
  throw new Error(`Unknown component type ${n}`);
}
const Cr = X(Na, {
  props: ["config", "vforSetting", "slotSetting"]
});
function Na(e) {
  const { config: t, vforSetting: n, slotSetting: r } = e, { items: s } = t, { bindingGetter: o } = aa(t, { vforSetting: n, slotSetting: r });
  return () => {
    if (o.updateVForInfo(e.vforSetting), o.updateSlotInfo(e.slotSetting), !s)
      return null;
    if (s.length === 1) {
      const i = s[0];
      return we(i, { sid: t.id, bindingGetter: o });
    }
    return s == null ? void 0 : s.map(
      (i) => we(i, { sid: t.id, bindingGetter: o })
    );
  };
}
function Va(e, t) {
  const { state: n, isReady: r, isLoading: s } = qs(async () => {
    let o = e;
    const i = t;
    if (!o && !i)
      throw new Error("Either config or configUrl must be provided");
    if (!o && i && (o = await (await fetch(i)).json()), !o)
      throw new Error("Failed to load config");
    return o;
  }, {});
  return { config: n, isReady: r, isLoading: s };
}
function Ca(e) {
  const t = L(!1), n = L("");
  function r(s, o) {
    let i;
    return o.component ? i = `Error captured from component:tag: ${o.component.tag} ; id: ${o.component.id} ` : i = "Error captured from app init", console.group(i), console.error("Component:", o.component), console.error("Error:", s), console.groupEnd(), e && (t.value = !0, n.value = `${i} ${s.message}`), !1;
  }
  return Jr(r), { hasError: t, errorMessage: n };
}
function Aa(e) {
  if (!(e === "web" || e === "webview") && e !== "zero")
    throw new Error(`Unsupported mode: ${e}`);
}
function xa(e, t) {
  const n = B(() => {
    const r = e.value;
    if (!r)
      return null;
    const i = new DOMParser().parseFromString(r, "image/svg+xml").querySelector("svg");
    if (!i)
      throw new Error("Invalid svg string");
    const a = {};
    for (const f of i.attributes)
      a[f.name] = f.value;
    const { size: c, color: d, attrs: u } = t;
    d.value !== null && d.value !== void 0 && (i.removeAttribute("fill"), i.querySelectorAll("*").forEach((h) => {
      h.hasAttribute("fill") && h.setAttribute("fill", "currentColor");
    }), a.color = d.value), c.value !== null && c.value !== void 0 && (a.width = c.value.toString(), a.height = c.value.toString());
    const l = i.innerHTML;
    return {
      ...a,
      ...u,
      innerHTML: l
    };
  });
  return () => {
    if (!n.value)
      return null;
    const r = n.value;
    return q("svg", r);
  };
}
const gn = "assets/icons";
async function $a(e) {
  if (!e) return;
  const { names: t, sets: n } = e, r = [];
  if (t) {
    const o = {}, i = [];
    for (const a of t) {
      if (!a.includes(":")) {
        i.push(a);
        continue;
      }
      const [c, d] = a.split(":");
      o[c] || (o[c] = []), o[c].push(d);
    }
    i.length > 0 && console.warn(`Invalid icon names (missing file prefix): ${i.join(", ")}`);
    for (const a of Object.keys(o)) {
      const c = `/${gn}/${a}.svg`, d = await fetch(c);
      if (!d.ok) throw new Error(`Failed to load ${c}`);
      const u = await d.text(), f = new DOMParser().parseFromString(u, "image/svg+xml");
      for (const h of o[a]) {
        const p = f.getElementById(h);
        if (!p) {
          console.warn(`Failed to find icon ${h} in ${c}`);
          continue;
        }
        p.setAttribute("id", `${a}:${h}`), r.push(p.outerHTML);
      }
    }
  }
  if (n)
    for (const o of n) {
      const i = `/${gn}/${o}.svg`, a = await fetch(i);
      if (!a.ok) throw new Error(`Failed to load ${i}`);
      const c = await a.text(), u = new DOMParser().parseFromString(c, "image/svg+xml"), l = Array.from(u.querySelectorAll("symbol"));
      if (l.length === 0) {
        console.warn(`No <symbol> found in ${i}`);
        continue;
      }
      for (const f of l) {
        const h = f.getAttribute("id");
        h && (f.setAttribute("id", `${o}:${h}`), r.push(f.outerHTML));
      }
    }
  const s = `<svg xmlns="http://www.w3.org/2000/svg" style="display:none">
${r.join(
    `
`
  )}
</svg>`;
  document.body.insertAdjacentHTML("afterbegin", s);
}
const Ta = {
  class: "app-box insta-theme",
  "data-scaling": "100%"
}, Ia = {
  key: 0,
  style: { position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)" }
}, Da = {
  key: 0,
  style: { color: "red", "font-size": "1.2em", margin: "1rem", border: "1px dashed red", padding: "1rem" }
}, Ma = /* @__PURE__ */ X({
  __name: "App",
  props: {
    config: {},
    meta: {},
    configUrl: {}
  },
  setup(e) {
    const t = e, { debug: n = !1 } = t.meta, { config: r, isLoading: s } = Va(
      t.config,
      t.configUrl
    );
    G(r, (a) => {
      a.url && (ts({
        mode: t.meta.mode,
        version: t.meta.version,
        queryPath: a.url.path,
        pathParams: a.url.params,
        webServerInfo: a.webInfo,
        debug: n
      }), hs(t.meta.mode), $a(a.icons)), Aa(t.meta.mode);
    });
    const { hasError: o, errorMessage: i } = Ca(n);
    return (a, c) => (ae(), ye("div", Ta, [
      Q(s) ? (ae(), ye("div", Ia, c[0] || (c[0] = [
        Nn("p", { style: { margin: "auto" } }, "Loading ...", -1)
      ]))) : (ae(), ye("div", {
        key: 1,
        class: dt(["insta-main", Q(r).class])
      }, [
        Qr(Q(Cr), {
          config: Q(r).scope
        }, null, 8, ["config"]),
        Q(o) ? (ae(), ye("div", Da, Sn(Q(i)), 1)) : ht("", !0)
      ], 2))
    ]));
  }
}), yn = /* @__PURE__ */ new Map([
  [
    "size",
    {
      classes: "ist-r-size",
      handler: (e) => Ba(e)
    }
  ],
  [
    "weight",
    {
      classes: "ist-r-weight",
      styleVar: "--weight",
      handler: (e) => e
    }
  ],
  [
    "text_align",
    {
      classes: "ist-r-ta",
      styleVar: "--ta",
      handler: (e) => e
    }
  ],
  [
    "trim",
    {
      classes: (e) => ja("ist-r", e)
    }
  ],
  [
    "truncate",
    {
      classes: "ist-r-truncate"
    }
  ],
  [
    "text_wrap",
    {
      classes: "ist-r-tw",
      handler: (e) => La(e)
    }
  ]
]);
function Ar(e) {
  const t = {}, n = [], r = {};
  for (const [o, i] of Object.entries(e)) {
    if (i === void 0 || !yn.has(o))
      continue;
    const a = typeof i == "object" ? i : { initial: i };
    for (const [c, d] of Object.entries(a)) {
      const { classes: u, styleVar: l, handler: f, propHandler: h } = yn.get(o), p = c === "initial";
      if (u) {
        const m = typeof u == "function" ? u(d) : u, y = p ? m : `${c}:${m}`;
        n.push(y);
      }
      if (f) {
        const m = f(d);
        if (l) {
          const y = p ? l : `${l}-${c}`;
          t[y] = m;
        } else {
          if (!Array.isArray(m))
            throw new Error(`Invalid style value: ${m}`);
          m.forEach((y) => {
            for (const [w, _] of Object.entries(y))
              t[w] = _;
          });
        }
      }
      if (h) {
        const m = h(d);
        for (const [y, w] of Object.entries(m))
          r[y] = w;
      }
    }
  }
  return {
    classes: n.join(" "),
    style: t,
    props: r
  };
}
function Ba(e) {
  const t = Number(e);
  if (isNaN(t))
    throw new Error(`Invalid font size value: ${e}`);
  return [
    { "--fs": `var(--font-size-${t})` },
    { "--lh": `var(--line-height-${t})` },
    { "--ls": `var(--letter-spacing-${t})` }
  ];
}
function ja(e, t) {
  return `${e}-lt-${t}`;
}
function La(e) {
  if (e === "wrap")
    return [
      {
        "--ws": "normal"
      }
    ];
  if (e === "nowrap")
    return [
      {
        "--ws": "nowrap"
      }
    ];
  if (e === "pretty")
    return [{ "--ws": "normal" }, { "--tw": "pretty" }];
  if (e === "balance")
    return [{ "--ws": "normal" }, { "--tw": "balance" }];
  throw new Error(`Invalid text wrap value: ${e}`);
}
const Fa = "insta-Heading", Ua = X(Wa, {
  props: [
    "as",
    "as_child",
    "size",
    "weight",
    "align",
    "trim",
    "truncate",
    "text_wrap",
    "innerText"
  ]
});
function Wa(e) {
  return () => {
    const { classes: t, style: n, props: r } = Ar(e), s = he(
      { class: t, style: n, ...r },
      { class: Fa }
    );
    return q(e.as || "h1", s, e.innerText);
  };
}
const za = /* @__PURE__ */ X({
  __name: "_Teleport",
  props: {
    to: {},
    defer: { type: Boolean, default: !0 },
    disabled: { type: Boolean, default: !1 }
  },
  setup(e) {
    return (t, n) => (ae(), Vn(Yr, {
      to: t.to,
      defer: t.defer,
      disabled: t.disabled
    }, [
      pt(t.$slots, "default")
    ], 8, ["to", "defer", "disabled"]));
  }
}), Ha = ["width", "height", "color"], Ka = ["xlink:href"], Ga = /* @__PURE__ */ X({
  __name: "Icon",
  props: {
    size: {},
    icon: {},
    color: {},
    assetPath: {},
    svgName: {},
    rawSvg: {}
  },
  setup(e) {
    const t = e, n = ge(() => t.icon ? t.icon.split(":")[1] : ""), r = ge(() => t.size || "1em"), s = ge(() => t.color || "currentColor"), o = ge(() => t.rawSvg || null), i = B(() => `#${t.icon}`), a = Pn(), c = xa(o, {
      size: ge(() => t.size),
      color: ge(() => t.color),
      attrs: a
    });
    return (d, u) => (ae(), ye(Xr, null, [
      n.value ? (ae(), ye("svg", he({
        key: 0,
        width: r.value,
        height: r.value,
        color: s.value
      }, Q(a)), [
        Nn("use", { "xlink:href": i.value }, null, 8, Ka)
      ], 16, Ha)) : ht("", !0),
      o.value ? (ae(), Vn(Q(c), { key: 1 })) : ht("", !0)
    ], 64));
  }
}), $e = /* @__PURE__ */ new Map([
  [
    "p",
    {
      classes: "ist-r-p",
      styleVar: "--p",
      handler: (e) => j("space", e)
    }
  ],
  [
    "px",
    {
      classes: "ist-r-px",
      styleVar: "--px",
      handler: (e) => j("space", e)
    }
  ],
  [
    "py",
    {
      classes: "ist-r-py",
      styleVar: "--py",
      handler: (e) => j("space", e)
    }
  ],
  [
    "pt",
    {
      classes: "ist-r-pt",
      styleVar: "--pt",
      handler: (e) => j("space", e)
    }
  ],
  [
    "pb",
    {
      classes: "ist-r-pb",
      styleVar: "--pb",
      handler: (e) => j("space", e)
    }
  ],
  [
    "pl",
    {
      classes: "ist-r-pl",
      styleVar: "--pl",
      handler: (e) => j("space", e)
    }
  ],
  [
    "pr",
    {
      classes: "ist-r-pr",
      styleVar: "--pr",
      handler: (e) => j("space", e)
    }
  ],
  [
    "width",
    {
      classes: "ist-r-w",
      styleVar: "--width",
      handler: (e) => e
    }
  ],
  [
    "height",
    {
      classes: "ist-r-h",
      styleVar: "--height",
      handler: (e) => e
    }
  ],
  [
    "min_width",
    {
      classes: "ist-r-min-w",
      styleVar: "--min_width",
      handler: (e) => e
    }
  ],
  [
    "min_height",
    {
      classes: "ist-r-min-h",
      styleVar: "--min_height",
      handler: (e) => e
    }
  ],
  [
    "max_width",
    {
      classes: "ist-r-max-w",
      styleVar: "--max_width",
      handler: (e) => e
    }
  ],
  [
    "max_height",
    {
      classes: "ist-r-max-h",
      styleVar: "--max_height",
      handler: (e) => e
    }
  ],
  [
    "position",
    {
      classes: "ist-r-position",
      styleVar: "--position",
      handler: (e) => e
    }
  ],
  [
    "inset",
    {
      classes: "ist-r-inset",
      styleVar: "--inset",
      handler: (e) => j("space", e)
    }
  ],
  [
    "top",
    {
      classes: "ist-r-top",
      styleVar: "--top",
      handler: (e) => j("space", e)
    }
  ],
  [
    "right",
    {
      classes: "ist-r-right",
      styleVar: "--right",
      handler: (e) => j("space", e)
    }
  ],
  [
    "bottom",
    {
      classes: "ist-r-bottom",
      styleVar: "--bottom",
      handler: (e) => j("space", e)
    }
  ],
  [
    "left",
    {
      classes: "ist-r-left",
      styleVar: "--left",
      handler: (e) => j("space", e)
    }
  ],
  [
    "overflow",
    {
      classes: "ist-r-overflow",
      styleVar: "--overflow",
      handler: (e) => e
    }
  ],
  [
    "overflow_x",
    {
      classes: "ist-r-ox",
      styleVar: "--overflow_x",
      handler: (e) => e
    }
  ],
  [
    "overflow_y",
    {
      classes: "ist-r-oy",
      styleVar: "--overflow_y",
      handler: (e) => e
    }
  ],
  [
    "flex_basis",
    {
      classes: "ist-r-fb",
      styleVar: "--flex_basis",
      handler: (e) => e
    }
  ],
  [
    "flex_shrink",
    {
      classes: "ist-r-fs",
      styleVar: "--flex_shrink",
      handler: (e) => e
    }
  ],
  [
    "flex_grow",
    {
      classes: "ist-r-fg",
      styleVar: "--flex_grow",
      handler: (e) => e
    }
  ],
  [
    "grid_area",
    {
      classes: "ist-r-ga",
      styleVar: "--grid_area",
      handler: (e) => e
    }
  ],
  [
    "grid_column",
    {
      classes: "ist-r-gc",
      styleVar: "--grid_column",
      handler: (e) => e
    }
  ],
  [
    "grid_column_start",
    {
      classes: "ist-r-gcs",
      styleVar: "--grid_column_start",
      handler: (e) => e
    }
  ],
  [
    "grid_column_end",
    {
      classes: "ist-r-gce",
      styleVar: "--grid_column_end",
      handler: (e) => e
    }
  ],
  [
    "grid_row",
    {
      classes: "ist-r-gr",
      styleVar: "--grid_row",
      handler: (e) => e
    }
  ],
  [
    "grid_row_start",
    {
      classes: "ist-r-grs",
      styleVar: "--grid_row_start",
      handler: (e) => e
    }
  ],
  [
    "grid_row_end",
    {
      classes: "ist-r-gre",
      styleVar: "--grid_row_end",
      handler: (e) => e
    }
  ],
  [
    "m",
    {
      classes: "ist-r-m",
      styleVar: "--m",
      handler: (e) => j("space", e)
    }
  ],
  [
    "mx",
    {
      classes: "ist-r-mx",
      styleVar: "--mx",
      handler: (e) => j("space", e)
    }
  ],
  [
    "my",
    {
      classes: "ist-r-my",
      styleVar: "--my",
      handler: (e) => j("space", e)
    }
  ],
  [
    "mt",
    {
      classes: "ist-r-mt",
      styleVar: "--mt",
      handler: (e) => j("space", e)
    }
  ],
  [
    "mr",
    {
      classes: "ist-r-mr",
      styleVar: "--mr",
      handler: (e) => j("space", e)
    }
  ],
  [
    "mb",
    {
      classes: "ist-r-mb",
      styleVar: "--mb",
      handler: (e) => j("space", e)
    }
  ],
  [
    "ml",
    {
      classes: "ist-r-ml",
      styleVar: "--ml",
      handler: (e) => j("space", e)
    }
  ],
  [
    "display",
    {
      classes: "ist-r-display",
      styleVar: "--display",
      handler: (e) => e
    }
  ],
  [
    "direction",
    {
      classes: "ist-r-fd",
      styleVar: "--direction",
      handler: (e) => e
    }
  ],
  [
    "align",
    {
      classes: "ist-r-ai",
      styleVar: "--align",
      handler: (e) => e
    }
  ],
  [
    "justify",
    {
      classes: "ist-r-jc",
      styleVar: "--justify",
      handler: (e) => e
    }
  ],
  [
    "wrap",
    {
      classes: "ist-r-wrap",
      styleVar: "--wrap",
      handler: (e) => e
    }
  ],
  [
    "gap",
    {
      classes: "ist-r-gap",
      styleVar: "--gap",
      handler: (e) => j("space", e)
    }
  ],
  [
    "gap_x",
    {
      classes: "ist-r-cg",
      styleVar: "--gap_x",
      handler: (e) => j("space", e)
    }
  ],
  [
    "gap_y",
    {
      classes: "ist-r-rg",
      styleVar: "--gap_y",
      handler: (e) => j("space", e)
    }
  ],
  [
    "areas",
    {
      classes: "ist-r-gta",
      styleVar: "--areas",
      handler: (e) => e
    }
  ],
  [
    "columns",
    {
      classes: "ist-r-gtc",
      styleVar: "--columns",
      handler: (e) => vn(e)
    }
  ],
  [
    "rows",
    {
      classes: "ist-r-gtr",
      styleVar: "--rows",
      handler: (e) => vn(e)
    }
  ],
  [
    "flow",
    {
      classes: "ist-r-gaf",
      styleVar: "--flow",
      handler: (e) => e
    }
  ],
  [
    "ctn_size",
    {
      classes: "ist-r-ctn_size",
      styleVar: "--ctn_size",
      handler: (e) => j("container", e)
    }
  ]
]);
function Xe(e) {
  e.length > 1 && console.warn("Only accept one child element when as_child is true");
}
function Ze(e) {
  return Object.fromEntries(
    Object.entries(e).filter(([t, n]) => n !== void 0)
  );
}
function et(e, t) {
  const n = {}, r = [], s = new Set(t || []), o = {
    style: {},
    class: []
  };
  for (const [a, c] of Object.entries(e)) {
    if (!$e.has(a))
      continue;
    const d = typeof c == "object" ? c : { initial: c };
    for (const [u, l] of Object.entries(d)) {
      const { classes: f, styleVar: h, handler: p } = $e.get(a), m = u === "initial", y = m ? f : `${u}:${f}`, w = m ? h : `${h}-${u}`, _ = p(l);
      if (s.has(a)) {
        o.class.push(y), o.style[w] = _;
        continue;
      }
      r.push(y), n[w] = _;
    }
  }
  return {
    classes: r.join(" "),
    style: n,
    excludeReslut: o
  };
}
function j(e, t) {
  const n = Number(t);
  if (isNaN(n))
    return t;
  {
    const r = n < 0 ? -1 : 1;
    return `calc(var(--${e}-${n}) * ${r})`;
  }
}
function vn(e) {
  const t = Number(e);
  return isNaN(t) ? e : `repeat(${t}, 1fr)`;
}
const tt = [
  "p",
  "px",
  "py",
  "pt",
  "pb",
  "pl",
  "pr",
  "width",
  "height",
  "min_width",
  "min_height",
  "max_width",
  "max_height",
  "position",
  "inset",
  "top",
  "right",
  "bottom",
  "left",
  "overflow",
  "overflow_x",
  "overflow_y",
  "flex_basis",
  "flex_shrink",
  "flex_grow",
  "grid_area",
  "grid_column",
  "grid_column_start",
  "grid_column_end",
  "grid_row",
  "grid_row_start",
  "grid_row_end",
  "m",
  "mx",
  "my",
  "mt",
  "mr",
  "mb",
  "ml"
], qa = [
  "as",
  "as_child",
  "display",
  "align",
  "justify",
  "wrap",
  "gap",
  "gap_x",
  "gap_y"
].concat(tt), Ja = ["direction"].concat(qa), Qa = [
  "as_child",
  "size",
  "display",
  "align",
  "ctn_size"
].concat(tt), Ya = ["as", "as_child", "display"].concat(tt), Xa = [
  "as",
  "as_child",
  "display",
  "areas",
  "columns",
  "rows",
  "flow",
  "align",
  "justify",
  "gap",
  "gap_x",
  "gap_y"
].concat(tt), Za = "insta-Box", ec = X(tc, {
  props: Ya
});
function tc(e) {
  const t = De();
  return () => {
    var a;
    const n = Ze(e), { classes: r, style: s } = et(n), o = he(
      { class: r, style: s },
      { class: Za }
    ), i = (a = t.default) == null ? void 0 : a.call(t);
    return e.as_child && i && i.length > 0 ? (Xe(i), re(i[0], o)) : q(e.as || "div", o, i);
  };
}
const nc = "insta-Flex", rc = {
  gap: "2"
}, sc = X(oc, {
  props: Ja
});
function oc(e) {
  const t = De();
  return () => {
    var a;
    const n = { ...rc, ...Ze(e) }, { classes: r, style: s } = et(n), o = he(
      { class: r, style: s },
      { class: nc }
    ), i = (a = t.default) == null ? void 0 : a.call(t);
    return e.as_child && i && i.length > 0 ? (Xe(i), re(i[0], o)) : q(e.as || "div", o, i);
  };
}
const ic = "insta-Grid", ac = {
  gap: "2"
}, cc = X(lc, {
  props: Xa
});
function lc(e) {
  const t = De();
  return () => {
    var c;
    const n = { ...ac, ...Ze(e) }, r = et(n), [s, o] = uc(r.classes, r.style), i = he(
      { class: s, style: o },
      { class: ic }
    ), a = (c = t.default) == null ? void 0 : c.call(t);
    return e.as_child && a && a.length > 0 ? (Xe(a), re(a[0], i)) : q(e.as || "div", i, a);
  };
}
function uc(e, t) {
  const n = $e.get("areas").styleVar, r = $e.get("columns").styleVar, s = n in t, o = r in t;
  if (!s || o)
    return [e, t];
  const i = fc(t[n]);
  if (i) {
    const { classes: a, styleVar: c } = $e.get("columns");
    e = `${e} ${a}`, t[c] = i;
  }
  return [e, t];
}
function fc(e) {
  if (typeof e != "string") return null;
  const t = [...e.matchAll(/"([^"]+)"/g)].map((i) => i[1]);
  if (t.length === 0) return null;
  const s = t[0].trim().split(/\s+/).length;
  return t.every(
    (i) => i.trim().split(/\s+/).length === s
  ) ? `repeat(${s}, 1fr)` : null;
}
const dc = "insta-Container", hc = X(pc, {
  props: Qa
});
function pc(e) {
  const t = De();
  return () => {
    var d;
    const n = Ze(e), { classes: r, style: s, excludeReslut: o } = et(n, [
      "ctn_size"
    ]), i = he(
      { class: r, style: s },
      { class: dc }
    ), a = (d = t.default) == null ? void 0 : d.call(t);
    if (e.as_child && a && a.length > 0)
      return Xe(a), re(a[0], i);
    const c = q(
      "div",
      he({ class: "insta-ContainerInner" }, o),
      a
    );
    return q("div", i, c);
  };
}
const mc = "insta-Text", gc = X(yc, {
  props: [
    "as",
    "as_child",
    "size",
    "weight",
    "align",
    "trim",
    "truncate",
    "text_wrap",
    "innerText"
  ]
});
function yc(e) {
  return () => {
    const { classes: t, style: n, props: r } = Ar(e), s = he(
      { class: t, style: n, ...r },
      { class: mc }
    );
    return q(e.as || "span", s, e.innerText);
  };
}
const wn = "insta-Link", vc = X(wc, {
  props: ["href", "text", "target", "type"]
});
function wc(e) {
  const t = De().default;
  return () => {
    const n = t ? [wn, "has-child"] : [wn], r = {
      href: e.href,
      target: e.target,
      type: e.type,
      class: n
    };
    return q("a", r, t ? t() : e.text);
  };
}
const ft = /* @__PURE__ */ new Map();
function _c(e, t, n, r) {
  const s = `${e}|${n ?? ""}`;
  if (ft.has(s))
    return ft.get(s);
  const o = /* @__PURE__ */ new WeakMap(), a = { observer: new IntersectionObserver(
    (c) => {
      for (const d of c) {
        const u = o.get(d.target);
        u && u(d.isIntersecting);
      }
    },
    {
      root: r,
      rootMargin: e,
      threshold: t
    }
  ), callbacks: o };
  return ft.set(s, a), a;
}
function Ec(e, t, n) {
  const r = n.margin ?? "0px", s = n.threshold ?? 0;
  let o = null;
  const i = () => {
    if (!e.value || n.enabled.value === !1) return;
    let d = null;
    n.rootSelector && (d = document.querySelector(n.rootSelector)), o = _c(
      r,
      s,
      n.rootSelector,
      d
    ), o.callbacks.set(e.value, t), o.observer.observe(e.value);
  }, a = () => {
    o && e.value && (o.observer.unobserve(e.value), o.callbacks.delete(e.value));
  }, c = () => {
    if (e.value) {
      if (!o) {
        i();
        return;
      }
      o.callbacks.set(e.value, t), o.observer.observe(e.value);
    }
  };
  At(() => {
    i();
  }), On(() => {
    o && e.value && (o.observer.unobserve(e.value), o.callbacks.delete(e.value));
  }), G(
    () => n.enabled.value,
    (d, u) => {
      d !== u && (d ? c() : a());
    },
    { immediate: !1 }
  );
}
const bc = /* @__PURE__ */ X({
  __name: "Lazy-Render",
  props: {
    height: {
      type: String,
      default: "200px"
    },
    destroyOnLeave: {
      type: Boolean,
      default: !0
    },
    margin: {
      type: String,
      default: "0px"
    },
    root: {
      type: String,
      default: void 0
    },
    disable: {
      type: Boolean,
      default: !1
    }
  },
  emits: ["visibility"],
  setup(e, { emit: t }) {
    const n = t, r = e, s = Zr("container"), o = L(!1), i = B(() => !r.disable);
    return Ec(
      s,
      (a) => {
        n("visibility", a), a ? o.value = !0 : r.destroyOnLeave && (o.value = !1);
      },
      {
        margin: r.margin,
        rootSelector: r.root,
        enabled: i
      }
    ), (a, c) => (ae(), ye("div", {
      ref_key: "container",
      ref: s,
      style: En({ minHeight: e.height, position: "relative" })
    }, [
      o.value ? pt(a.$slots, "default", { key: 0 }) : pt(a.$slots, "hidden", { key: 1 })
    ], 4));
  }
});
function Sc(e, t) {
  const { mode: n = "hash" } = t.router, r = n === "hash" ? hi() : n === "memory" ? di() : yr();
  e.use(
    ra({
      history: r,
      routes: kc(t)
    })
  );
}
function kc(e) {
  if (!e.router)
    throw new Error("Router config is not provided.");
  const { routes: t = [], kAlive: n = !1 } = e.router;
  return t.map(
    (s) => xr(s, n)
  );
}
function xr(e, t) {
  const {
    server: n = !1,
    vueItem: r,
    scope: s,
    children: o
  } = e, i = () => {
    if (n)
      throw new Error("Server-side rendering is not supported yet.");
    return Promise.resolve(Rc(e, t));
  }, a = o == null ? void 0 : o.map(
    (d) => xr(d, t)
  ), c = {
    ...r,
    children: a,
    component: i
  };
  return s || delete c.component, a || delete c.children, c;
}
function Rc(e, t) {
  const { scope: n } = e;
  if (!n)
    throw new Error("Scope is not provided.");
  const r = re(Me(n), { key: n.id });
  return t ? q(es, null, () => r) : r;
}
function Vc(e, t) {
  e.component("insta-ui", Ma), e.component("teleport", za), e.component("icon", Ga), e.component("heading", Ua), e.component("box", ec), e.component("flex", sc), e.component("grid", cc), e.component("container", hc), e.component("ui-text", gc), e.component("ui-link", vc), e.component("lazy-render", bc), t.router && Sc(e, t);
}
export {
  He as convertDynamicProperties,
  We as getAppInfo,
  Vc as install,
  Nc as useBindingGetter,
  fo as useLanguage
};
