import { i as ui, a as Kt, r as di, b as fi, Z as it, g as hi, c as K, d as pi, e as mi, o as gi } from "./Index-BiZKFasJ.js";
const _ = window.ms_globals.React, f = window.ms_globals.React, ri = window.ms_globals.React.forwardRef, he = window.ms_globals.React.useRef, $e = window.ms_globals.React.useState, Ce = window.ms_globals.React.useEffect, ii = window.ms_globals.React.version, oi = window.ms_globals.React.isValidElement, si = window.ms_globals.React.useLayoutEffect, ai = window.ms_globals.React.useImperativeHandle, li = window.ms_globals.React.memo, qt = window.ms_globals.React.useMemo, ci = window.ms_globals.React.useCallback, mn = window.ms_globals.ReactDOM, ut = window.ms_globals.ReactDOM.createPortal, vi = window.ms_globals.internalContext.useContextPropsContext, bi = window.ms_globals.internalContext.useSuggestionOpenContext, ur = window.ms_globals.antdIcons.FileTextFilled, yi = window.ms_globals.antdIcons.CloseCircleFilled, wi = window.ms_globals.antdIcons.FileExcelFilled, Si = window.ms_globals.antdIcons.FileImageFilled, xi = window.ms_globals.antdIcons.FileMarkdownFilled, Ci = window.ms_globals.antdIcons.FilePdfFilled, Ei = window.ms_globals.antdIcons.FilePptFilled, _i = window.ms_globals.antdIcons.FileWordFilled, Ri = window.ms_globals.antdIcons.FileZipFilled, Pi = window.ms_globals.antdIcons.PlusOutlined, Ti = window.ms_globals.antdIcons.LeftOutlined, Mi = window.ms_globals.antdIcons.RightOutlined, Li = window.ms_globals.antdIcons.CloseOutlined, Oi = window.ms_globals.antdIcons.ClearOutlined, Ai = window.ms_globals.antdIcons.ArrowUpOutlined, Ii = window.ms_globals.antdIcons.AudioMutedOutlined, $i = window.ms_globals.antdIcons.AudioOutlined, ki = window.ms_globals.antdIcons.LinkOutlined, Di = window.ms_globals.antdIcons.CloudUploadOutlined, Fi = window.ms_globals.antd.ConfigProvider, dt = window.ms_globals.antd.theme, dr = window.ms_globals.antd.Upload, Ni = window.ms_globals.antd.Progress, ji = window.ms_globals.antd.Image, ke = window.ms_globals.antd.Button, ft = window.ms_globals.antd.Flex, It = window.ms_globals.antd.Typography, Wi = window.ms_globals.antd.Input, Bi = window.ms_globals.antd.Tooltip, Hi = window.ms_globals.antd.Badge, Yt = window.ms_globals.antdCssinjs.unit, $t = window.ms_globals.antdCssinjs.token2CSSVar, gn = window.ms_globals.antdCssinjs.useStyleRegister, zi = window.ms_globals.antdCssinjs.useCSSVarRegister, Ui = window.ms_globals.antdCssinjs.createTheme, Vi = window.ms_globals.antdCssinjs.useCacheToken;
var Xi = /\s/;
function Gi(n) {
  for (var e = n.length; e-- && Xi.test(n.charAt(e)); )
    ;
  return e;
}
var qi = /^\s+/;
function Ki(n) {
  return n && n.slice(0, Gi(n) + 1).replace(qi, "");
}
var vn = NaN, Yi = /^[-+]0x[0-9a-f]+$/i, Zi = /^0b[01]+$/i, Qi = /^0o[0-7]+$/i, Ji = parseInt;
function bn(n) {
  if (typeof n == "number")
    return n;
  if (ui(n))
    return vn;
  if (Kt(n)) {
    var e = typeof n.valueOf == "function" ? n.valueOf() : n;
    n = Kt(e) ? e + "" : e;
  }
  if (typeof n != "string")
    return n === 0 ? n : +n;
  n = Ki(n);
  var t = Zi.test(n);
  return t || Qi.test(n) ? Ji(n.slice(2), t ? 2 : 8) : Yi.test(n) ? vn : +n;
}
function eo() {
}
var kt = function() {
  return di.Date.now();
}, to = "Expected a function", no = Math.max, ro = Math.min;
function io(n, e, t) {
  var r, i, o, s, a, c, l = 0, u = !1, d = !1, h = !0;
  if (typeof n != "function")
    throw new TypeError(to);
  e = bn(e) || 0, Kt(t) && (u = !!t.leading, d = "maxWait" in t, o = d ? no(bn(t.maxWait) || 0, e) : o, h = "trailing" in t ? !!t.trailing : h);
  function p(x) {
    var T = r, R = i;
    return r = i = void 0, l = x, s = n.apply(R, T), s;
  }
  function v(x) {
    return l = x, a = setTimeout(b, e), u ? p(x) : s;
  }
  function g(x) {
    var T = x - c, R = x - l, O = e - T;
    return d ? ro(O, o - R) : O;
  }
  function m(x) {
    var T = x - c, R = x - l;
    return c === void 0 || T >= e || T < 0 || d && R >= o;
  }
  function b() {
    var x = kt();
    if (m(x))
      return w(x);
    a = setTimeout(b, g(x));
  }
  function w(x) {
    return a = void 0, h && r ? p(x) : (r = i = void 0, s);
  }
  function C() {
    a !== void 0 && clearTimeout(a), l = 0, r = c = i = a = void 0;
  }
  function E() {
    return a === void 0 ? s : w(kt());
  }
  function S() {
    var x = kt(), T = m(x);
    if (r = arguments, i = this, c = x, T) {
      if (a === void 0)
        return v(c);
      if (d)
        return clearTimeout(a), a = setTimeout(b, e), p(c);
    }
    return a === void 0 && (a = setTimeout(b, e)), s;
  }
  return S.cancel = C, S.flush = E, S;
}
function oo(n, e) {
  return fi(n, e);
}
var fr = {
  exports: {}
}, gt = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var so = f, ao = Symbol.for("react.element"), lo = Symbol.for("react.fragment"), co = Object.prototype.hasOwnProperty, uo = so.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, fo = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function hr(n, e, t) {
  var r, i = {}, o = null, s = null;
  t !== void 0 && (o = "" + t), e.key !== void 0 && (o = "" + e.key), e.ref !== void 0 && (s = e.ref);
  for (r in e) co.call(e, r) && !fo.hasOwnProperty(r) && (i[r] = e[r]);
  if (n && n.defaultProps) for (r in e = n.defaultProps, e) i[r] === void 0 && (i[r] = e[r]);
  return {
    $$typeof: ao,
    type: n,
    key: o,
    ref: s,
    props: i,
    _owner: uo.current
  };
}
gt.Fragment = lo;
gt.jsx = hr;
gt.jsxs = hr;
fr.exports = gt;
var q = fr.exports;
const {
  SvelteComponent: ho,
  assign: yn,
  binding_callbacks: wn,
  check_outros: po,
  children: pr,
  claim_element: mr,
  claim_space: mo,
  component_subscribe: Sn,
  compute_slots: go,
  create_slot: vo,
  detach: Oe,
  element: gr,
  empty: xn,
  exclude_internal_props: Cn,
  get_all_dirty_from_scope: bo,
  get_slot_changes: yo,
  group_outros: wo,
  init: So,
  insert_hydration: ot,
  safe_not_equal: xo,
  set_custom_element_data: vr,
  space: Co,
  transition_in: st,
  transition_out: Zt,
  update_slot_base: Eo
} = window.__gradio__svelte__internal, {
  beforeUpdate: _o,
  getContext: Ro,
  onDestroy: Po,
  setContext: To
} = window.__gradio__svelte__internal;
function En(n) {
  let e, t;
  const r = (
    /*#slots*/
    n[7].default
  ), i = vo(
    r,
    n,
    /*$$scope*/
    n[6],
    null
  );
  return {
    c() {
      e = gr("svelte-slot"), i && i.c(), this.h();
    },
    l(o) {
      e = mr(o, "SVELTE-SLOT", {
        class: !0
      });
      var s = pr(e);
      i && i.l(s), s.forEach(Oe), this.h();
    },
    h() {
      vr(e, "class", "svelte-1rt0kpf");
    },
    m(o, s) {
      ot(o, e, s), i && i.m(e, null), n[9](e), t = !0;
    },
    p(o, s) {
      i && i.p && (!t || s & /*$$scope*/
      64) && Eo(
        i,
        r,
        o,
        /*$$scope*/
        o[6],
        t ? yo(
          r,
          /*$$scope*/
          o[6],
          s,
          null
        ) : bo(
          /*$$scope*/
          o[6]
        ),
        null
      );
    },
    i(o) {
      t || (st(i, o), t = !0);
    },
    o(o) {
      Zt(i, o), t = !1;
    },
    d(o) {
      o && Oe(e), i && i.d(o), n[9](null);
    }
  };
}
function Mo(n) {
  let e, t, r, i, o = (
    /*$$slots*/
    n[4].default && En(n)
  );
  return {
    c() {
      e = gr("react-portal-target"), t = Co(), o && o.c(), r = xn(), this.h();
    },
    l(s) {
      e = mr(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), pr(e).forEach(Oe), t = mo(s), o && o.l(s), r = xn(), this.h();
    },
    h() {
      vr(e, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      ot(s, e, a), n[8](e), ot(s, t, a), o && o.m(s, a), ot(s, r, a), i = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? o ? (o.p(s, a), a & /*$$slots*/
      16 && st(o, 1)) : (o = En(s), o.c(), st(o, 1), o.m(r.parentNode, r)) : o && (wo(), Zt(o, 1, 1, () => {
        o = null;
      }), po());
    },
    i(s) {
      i || (st(o), i = !0);
    },
    o(s) {
      Zt(o), i = !1;
    },
    d(s) {
      s && (Oe(e), Oe(t), Oe(r)), n[8](null), o && o.d(s);
    }
  };
}
function _n(n) {
  const {
    svelteInit: e,
    ...t
  } = n;
  return t;
}
function Lo(n, e, t) {
  let r, i, {
    $$slots: o = {},
    $$scope: s
  } = e;
  const a = go(o);
  let {
    svelteInit: c
  } = e;
  const l = it(_n(e)), u = it();
  Sn(n, u, (E) => t(0, r = E));
  const d = it();
  Sn(n, d, (E) => t(1, i = E));
  const h = [], p = Ro("$$ms-gr-react-wrapper"), {
    slotKey: v,
    slotIndex: g,
    subSlotIndex: m
  } = hi() || {}, b = c({
    parent: p,
    props: l,
    target: u,
    slot: d,
    slotKey: v,
    slotIndex: g,
    subSlotIndex: m,
    onDestroy(E) {
      h.push(E);
    }
  });
  To("$$ms-gr-react-wrapper", b), _o(() => {
    l.set(_n(e));
  }), Po(() => {
    h.forEach((E) => E());
  });
  function w(E) {
    wn[E ? "unshift" : "push"](() => {
      r = E, u.set(r);
    });
  }
  function C(E) {
    wn[E ? "unshift" : "push"](() => {
      i = E, d.set(i);
    });
  }
  return n.$$set = (E) => {
    t(17, e = yn(yn({}, e), Cn(E))), "svelteInit" in E && t(5, c = E.svelteInit), "$$scope" in E && t(6, s = E.$$scope);
  }, e = Cn(e), [r, i, u, d, a, c, s, o, w, C];
}
class Oo extends ho {
  constructor(e) {
    super(), So(this, e, Lo, Mo, xo, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Al
} = window.__gradio__svelte__internal, Rn = window.ms_globals.rerender, Dt = window.ms_globals.tree;
function Ao(n, e = {}) {
  function t(r) {
    const i = it(), o = new Oo({
      ...r,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: i,
            reactComponent: n,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: e.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, c = s.parent ?? Dt;
          return c.nodes = [...c.nodes, a], Rn({
            createPortal: ut,
            node: Dt
          }), s.onDestroy(() => {
            c.nodes = c.nodes.filter((l) => l.svelteInstance !== i), Rn({
              createPortal: ut,
              node: Dt
            });
          }), a;
        },
        ...r.props
      }
    });
    return i.set(o), o;
  }
  return new Promise((r) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((i) => {
      window.ms_globals.initialize = () => {
        i();
      };
    })), window.ms_globals.initializePromise.then(() => {
      r(t);
    });
  });
}
const Io = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function $o(n) {
  return n ? Object.keys(n).reduce((e, t) => {
    const r = n[t];
    return e[t] = ko(t, r), e;
  }, {}) : {};
}
function ko(n, e) {
  return typeof e == "number" && !Io.includes(n) ? e + "px" : e;
}
function Qt(n) {
  const e = [], t = n.cloneNode(!1);
  if (n._reactElement) {
    const i = f.Children.toArray(n._reactElement.props.children).map((o) => {
      if (f.isValidElement(o) && o.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = Qt(o.props.el);
        return f.cloneElement(o, {
          ...o.props,
          el: a,
          children: [...f.Children.toArray(o.props.children), ...s]
        });
      }
      return null;
    });
    return i.originalChildren = n._reactElement.props.children, e.push(ut(f.cloneElement(n._reactElement, {
      ...n._reactElement.props,
      children: i
    }), t)), {
      clonedElement: t,
      portals: e
    };
  }
  Object.keys(n.getEventListeners()).forEach((i) => {
    n.getEventListeners(i).forEach(({
      listener: s,
      type: a,
      useCapture: c
    }) => {
      t.addEventListener(a, s, c);
    });
  });
  const r = Array.from(n.childNodes);
  for (let i = 0; i < r.length; i++) {
    const o = r[i];
    if (o.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = Qt(o);
      e.push(...a), t.appendChild(s);
    } else o.nodeType === 3 && t.appendChild(o.cloneNode());
  }
  return {
    clonedElement: t,
    portals: e
  };
}
function Do(n, e) {
  n && (typeof n == "function" ? n(e) : n.current = e);
}
const je = ri(({
  slot: n,
  clone: e,
  className: t,
  style: r,
  observeAttributes: i
}, o) => {
  const s = he(), [a, c] = $e([]), {
    forceClone: l
  } = vi(), u = l ? !0 : e;
  return Ce(() => {
    var g;
    if (!s.current || !n)
      return;
    let d = n;
    function h() {
      let m = d;
      if (d.tagName.toLowerCase() === "svelte-slot" && d.children.length === 1 && d.children[0] && (m = d.children[0], m.tagName.toLowerCase() === "react-portal-target" && m.children[0] && (m = m.children[0])), Do(o, m), t && m.classList.add(...t.split(" ")), r) {
        const b = $o(r);
        Object.keys(b).forEach((w) => {
          m.style[w] = b[w];
        });
      }
    }
    let p = null, v = null;
    if (u && window.MutationObserver) {
      let m = function() {
        var E, S, x;
        (E = s.current) != null && E.contains(d) && ((S = s.current) == null || S.removeChild(d));
        const {
          portals: w,
          clonedElement: C
        } = Qt(n);
        d = C, c(w), d.style.display = "contents", v && clearTimeout(v), v = setTimeout(() => {
          h();
        }, 50), (x = s.current) == null || x.appendChild(d);
      };
      m();
      const b = io(() => {
        m(), p == null || p.disconnect(), p == null || p.observe(n, {
          childList: !0,
          subtree: !0,
          attributes: i
        });
      }, 50);
      p = new window.MutationObserver(b), p.observe(n, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      d.style.display = "contents", h(), (g = s.current) == null || g.appendChild(d);
    return () => {
      var m, b;
      d.style.display = "", (m = s.current) != null && m.contains(d) && ((b = s.current) == null || b.removeChild(d)), p == null || p.disconnect();
    };
  }, [n, u, t, r, o, i, l]), f.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), Fo = "1.6.1";
function ve() {
  return ve = Object.assign ? Object.assign.bind() : function(n) {
    for (var e = 1; e < arguments.length; e++) {
      var t = arguments[e];
      for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]);
    }
    return n;
  }, ve.apply(null, arguments);
}
function _e(n) {
  "@babel/helpers - typeof";
  return _e = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, _e(n);
}
function No(n, e) {
  if (_e(n) != "object" || !n) return n;
  var t = n[Symbol.toPrimitive];
  if (t !== void 0) {
    var r = t.call(n, e);
    if (_e(r) != "object") return r;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(n);
}
function jo(n) {
  var e = No(n, "string");
  return _e(e) == "symbol" ? e : e + "";
}
function Wo(n, e, t) {
  return (e = jo(e)) in n ? Object.defineProperty(n, e, {
    value: t,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : n[e] = t, n;
}
function Pn(n, e) {
  var t = Object.keys(n);
  if (Object.getOwnPropertySymbols) {
    var r = Object.getOwnPropertySymbols(n);
    e && (r = r.filter(function(i) {
      return Object.getOwnPropertyDescriptor(n, i).enumerable;
    })), t.push.apply(t, r);
  }
  return t;
}
function Bo(n) {
  for (var e = 1; e < arguments.length; e++) {
    var t = arguments[e] != null ? arguments[e] : {};
    e % 2 ? Pn(Object(t), !0).forEach(function(r) {
      Wo(n, r, t[r]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(n, Object.getOwnPropertyDescriptors(t)) : Pn(Object(t)).forEach(function(r) {
      Object.defineProperty(n, r, Object.getOwnPropertyDescriptor(t, r));
    });
  }
  return n;
}
var Ho = `accept acceptCharset accessKey action allowFullScreen allowTransparency
    alt async autoComplete autoFocus autoPlay capture cellPadding cellSpacing challenge
    charSet checked classID className colSpan cols content contentEditable contextMenu
    controls coords crossOrigin data dateTime default defer dir disabled download draggable
    encType form formAction formEncType formMethod formNoValidate formTarget frameBorder
    headers height hidden high href hrefLang htmlFor httpEquiv icon id inputMode integrity
    is keyParams keyType kind label lang list loop low manifest marginHeight marginWidth max maxLength media
    mediaGroup method min minLength multiple muted name noValidate nonce open
    optimum pattern placeholder poster preload radioGroup readOnly rel required
    reversed role rowSpan rows sandbox scope scoped scrolling seamless selected
    shape size sizes span spellCheck src srcDoc srcLang srcSet start step style
    summary tabIndex target title type useMap value width wmode wrap`, zo = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, Uo = "".concat(Ho, " ").concat(zo).split(/[\s\n]+/), Vo = "aria-", Xo = "data-";
function Tn(n, e) {
  return n.indexOf(e) === 0;
}
function Go(n) {
  var e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, t;
  e === !1 ? t = {
    aria: !0,
    data: !0,
    attr: !0
  } : e === !0 ? t = {
    aria: !0
  } : t = Bo({}, e);
  var r = {};
  return Object.keys(n).forEach(function(i) {
    // Aria
    (t.aria && (i === "role" || Tn(i, Vo)) || // Data
    t.data && Tn(i, Xo) || // Attr
    t.attr && Uo.includes(i)) && (r[i] = n[i]);
  }), r;
}
const qo = /* @__PURE__ */ f.createContext({}), Ko = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, br = (n) => {
  const e = f.useContext(qo);
  return f.useMemo(() => ({
    ...Ko,
    ...e[n]
  }), [e[n]]);
};
function Ue() {
  const {
    getPrefixCls: n,
    direction: e,
    csp: t,
    iconPrefixCls: r,
    theme: i
  } = f.useContext(Fi.ConfigContext);
  return {
    theme: i,
    getPrefixCls: n,
    direction: e,
    csp: t,
    iconPrefixCls: r
  };
}
function fe(n) {
  "@babel/helpers - typeof";
  return fe = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, fe(n);
}
function Yo(n) {
  if (Array.isArray(n)) return n;
}
function Zo(n, e) {
  var t = n == null ? null : typeof Symbol < "u" && n[Symbol.iterator] || n["@@iterator"];
  if (t != null) {
    var r, i, o, s, a = [], c = !0, l = !1;
    try {
      if (o = (t = t.call(n)).next, e === 0) {
        if (Object(t) !== t) return;
        c = !1;
      } else for (; !(c = (r = o.call(t)).done) && (a.push(r.value), a.length !== e); c = !0) ;
    } catch (u) {
      l = !0, i = u;
    } finally {
      try {
        if (!c && t.return != null && (s = t.return(), Object(s) !== s)) return;
      } finally {
        if (l) throw i;
      }
    }
    return a;
  }
}
function Mn(n, e) {
  (e == null || e > n.length) && (e = n.length);
  for (var t = 0, r = Array(e); t < e; t++) r[t] = n[t];
  return r;
}
function Qo(n, e) {
  if (n) {
    if (typeof n == "string") return Mn(n, e);
    var t = {}.toString.call(n).slice(8, -1);
    return t === "Object" && n.constructor && (t = n.constructor.name), t === "Map" || t === "Set" ? Array.from(n) : t === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? Mn(n, e) : void 0;
  }
}
function Jo() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function ge(n, e) {
  return Yo(n) || Zo(n, e) || Qo(n, e) || Jo();
}
function es(n, e) {
  if (fe(n) != "object" || !n) return n;
  var t = n[Symbol.toPrimitive];
  if (t !== void 0) {
    var r = t.call(n, e);
    if (fe(r) != "object") return r;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(n);
}
function yr(n) {
  var e = es(n, "string");
  return fe(e) == "symbol" ? e : e + "";
}
function D(n, e, t) {
  return (e = yr(e)) in n ? Object.defineProperty(n, e, {
    value: t,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : n[e] = t, n;
}
function Ln(n, e) {
  var t = Object.keys(n);
  if (Object.getOwnPropertySymbols) {
    var r = Object.getOwnPropertySymbols(n);
    e && (r = r.filter(function(i) {
      return Object.getOwnPropertyDescriptor(n, i).enumerable;
    })), t.push.apply(t, r);
  }
  return t;
}
function k(n) {
  for (var e = 1; e < arguments.length; e++) {
    var t = arguments[e] != null ? arguments[e] : {};
    e % 2 ? Ln(Object(t), !0).forEach(function(r) {
      D(n, r, t[r]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(n, Object.getOwnPropertyDescriptors(t)) : Ln(Object(t)).forEach(function(r) {
      Object.defineProperty(n, r, Object.getOwnPropertyDescriptor(t, r));
    });
  }
  return n;
}
function De(n, e) {
  if (!(n instanceof e)) throw new TypeError("Cannot call a class as a function");
}
function On(n, e) {
  for (var t = 0; t < e.length; t++) {
    var r = e[t];
    r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(n, yr(r.key), r);
  }
}
function Fe(n, e, t) {
  return e && On(n.prototype, e), t && On(n, t), Object.defineProperty(n, "prototype", {
    writable: !1
  }), n;
}
function Te(n) {
  if (n === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return n;
}
function Jt(n, e) {
  return Jt = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(t, r) {
    return t.__proto__ = r, t;
  }, Jt(n, e);
}
function vt(n, e) {
  if (typeof e != "function" && e !== null) throw new TypeError("Super expression must either be null or a function");
  n.prototype = Object.create(e && e.prototype, {
    constructor: {
      value: n,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(n, "prototype", {
    writable: !1
  }), e && Jt(n, e);
}
function ht(n) {
  return ht = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
    return e.__proto__ || Object.getPrototypeOf(e);
  }, ht(n);
}
function wr() {
  try {
    var n = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (wr = function() {
    return !!n;
  })();
}
function ts(n, e) {
  if (e && (fe(e) == "object" || typeof e == "function")) return e;
  if (e !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return Te(n);
}
function bt(n) {
  var e = wr();
  return function() {
    var t, r = ht(n);
    if (e) {
      var i = ht(this).constructor;
      t = Reflect.construct(r, arguments, i);
    } else t = r.apply(this, arguments);
    return ts(this, t);
  };
}
var Sr = /* @__PURE__ */ Fe(function n() {
  De(this, n);
}), xr = "CALC_UNIT", ns = new RegExp(xr, "g");
function Ft(n) {
  return typeof n == "number" ? "".concat(n).concat(xr) : n;
}
var rs = /* @__PURE__ */ function(n) {
  vt(t, n);
  var e = bt(t);
  function t(r, i) {
    var o;
    De(this, t), o = e.call(this), D(Te(o), "result", ""), D(Te(o), "unitlessCssVar", void 0), D(Te(o), "lowPriority", void 0);
    var s = fe(r);
    return o.unitlessCssVar = i, r instanceof t ? o.result = "(".concat(r.result, ")") : s === "number" ? o.result = Ft(r) : s === "string" && (o.result = r), o;
  }
  return Fe(t, [{
    key: "add",
    value: function(i) {
      return i instanceof t ? this.result = "".concat(this.result, " + ").concat(i.getResult()) : (typeof i == "number" || typeof i == "string") && (this.result = "".concat(this.result, " + ").concat(Ft(i))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(i) {
      return i instanceof t ? this.result = "".concat(this.result, " - ").concat(i.getResult()) : (typeof i == "number" || typeof i == "string") && (this.result = "".concat(this.result, " - ").concat(Ft(i))), this.lowPriority = !0, this;
    }
  }, {
    key: "mul",
    value: function(i) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), i instanceof t ? this.result = "".concat(this.result, " * ").concat(i.getResult(!0)) : (typeof i == "number" || typeof i == "string") && (this.result = "".concat(this.result, " * ").concat(i)), this.lowPriority = !1, this;
    }
  }, {
    key: "div",
    value: function(i) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), i instanceof t ? this.result = "".concat(this.result, " / ").concat(i.getResult(!0)) : (typeof i == "number" || typeof i == "string") && (this.result = "".concat(this.result, " / ").concat(i)), this.lowPriority = !1, this;
    }
  }, {
    key: "getResult",
    value: function(i) {
      return this.lowPriority || i ? "(".concat(this.result, ")") : this.result;
    }
  }, {
    key: "equal",
    value: function(i) {
      var o = this, s = i || {}, a = s.unit, c = !0;
      return typeof a == "boolean" ? c = a : Array.from(this.unitlessCssVar).some(function(l) {
        return o.result.includes(l);
      }) && (c = !1), this.result = this.result.replace(ns, c ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), t;
}(Sr), is = /* @__PURE__ */ function(n) {
  vt(t, n);
  var e = bt(t);
  function t(r) {
    var i;
    return De(this, t), i = e.call(this), D(Te(i), "result", 0), r instanceof t ? i.result = r.result : typeof r == "number" && (i.result = r), i;
  }
  return Fe(t, [{
    key: "add",
    value: function(i) {
      return i instanceof t ? this.result += i.result : typeof i == "number" && (this.result += i), this;
    }
  }, {
    key: "sub",
    value: function(i) {
      return i instanceof t ? this.result -= i.result : typeof i == "number" && (this.result -= i), this;
    }
  }, {
    key: "mul",
    value: function(i) {
      return i instanceof t ? this.result *= i.result : typeof i == "number" && (this.result *= i), this;
    }
  }, {
    key: "div",
    value: function(i) {
      return i instanceof t ? this.result /= i.result : typeof i == "number" && (this.result /= i), this;
    }
  }, {
    key: "equal",
    value: function() {
      return this.result;
    }
  }]), t;
}(Sr), os = function(e, t) {
  var r = e === "css" ? rs : is;
  return function(i) {
    return new r(i, t);
  };
}, An = function(e, t) {
  return "".concat([t, e.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function Re(n) {
  var e = _.useRef();
  e.current = n;
  var t = _.useCallback(function() {
    for (var r, i = arguments.length, o = new Array(i), s = 0; s < i; s++)
      o[s] = arguments[s];
    return (r = e.current) === null || r === void 0 ? void 0 : r.call.apply(r, [e].concat(o));
  }, []);
  return t;
}
function ss(n) {
  if (Array.isArray(n)) return n;
}
function as(n, e) {
  var t = n == null ? null : typeof Symbol < "u" && n[Symbol.iterator] || n["@@iterator"];
  if (t != null) {
    var r, i, o, s, a = [], c = !0, l = !1;
    try {
      if (o = (t = t.call(n)).next, e !== 0) for (; !(c = (r = o.call(t)).done) && (a.push(r.value), a.length !== e); c = !0) ;
    } catch (u) {
      l = !0, i = u;
    } finally {
      try {
        if (!c && t.return != null && (s = t.return(), Object(s) !== s)) return;
      } finally {
        if (l) throw i;
      }
    }
    return a;
  }
}
function In(n, e) {
  (e == null || e > n.length) && (e = n.length);
  for (var t = 0, r = Array(e); t < e; t++) r[t] = n[t];
  return r;
}
function ls(n, e) {
  if (n) {
    if (typeof n == "string") return In(n, e);
    var t = {}.toString.call(n).slice(8, -1);
    return t === "Object" && n.constructor && (t = n.constructor.name), t === "Map" || t === "Set" ? Array.from(n) : t === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? In(n, e) : void 0;
  }
}
function cs() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function pt(n, e) {
  return ss(n) || as(n, e) || ls(n, e) || cs();
}
function yt() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var $n = yt() ? _.useLayoutEffect : _.useEffect, us = function(e, t) {
  var r = _.useRef(!0);
  $n(function() {
    return e(r.current);
  }, t), $n(function() {
    return r.current = !1, function() {
      r.current = !0;
    };
  }, []);
}, kn = function(e, t) {
  us(function(r) {
    if (!r)
      return e();
  }, t);
};
function Ve(n) {
  var e = _.useRef(!1), t = _.useState(n), r = pt(t, 2), i = r[0], o = r[1];
  _.useEffect(function() {
    return e.current = !1, function() {
      e.current = !0;
    };
  }, []);
  function s(a, c) {
    c && e.current || o(a);
  }
  return [i, s];
}
function Nt(n) {
  return n !== void 0;
}
function cn(n, e) {
  var t = e || {}, r = t.defaultValue, i = t.value, o = t.onChange, s = t.postState, a = Ve(function() {
    return Nt(i) ? i : Nt(r) ? typeof r == "function" ? r() : r : typeof n == "function" ? n() : n;
  }), c = pt(a, 2), l = c[0], u = c[1], d = i !== void 0 ? i : l, h = s ? s(d) : d, p = Re(o), v = Ve([d]), g = pt(v, 2), m = g[0], b = g[1];
  kn(function() {
    var C = m[0];
    l !== C && p(l, C);
  }, [m]), kn(function() {
    Nt(i) || u(i);
  }, [i]);
  var w = Re(function(C, E) {
    u(C, E), b([d], E);
  });
  return [h, w];
}
var Cr = {
  exports: {}
}, H = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var un = Symbol.for("react.element"), dn = Symbol.for("react.portal"), wt = Symbol.for("react.fragment"), St = Symbol.for("react.strict_mode"), xt = Symbol.for("react.profiler"), Ct = Symbol.for("react.provider"), Et = Symbol.for("react.context"), ds = Symbol.for("react.server_context"), _t = Symbol.for("react.forward_ref"), Rt = Symbol.for("react.suspense"), Pt = Symbol.for("react.suspense_list"), Tt = Symbol.for("react.memo"), Mt = Symbol.for("react.lazy"), fs = Symbol.for("react.offscreen"), Er;
Er = Symbol.for("react.module.reference");
function be(n) {
  if (typeof n == "object" && n !== null) {
    var e = n.$$typeof;
    switch (e) {
      case un:
        switch (n = n.type, n) {
          case wt:
          case xt:
          case St:
          case Rt:
          case Pt:
            return n;
          default:
            switch (n = n && n.$$typeof, n) {
              case ds:
              case Et:
              case _t:
              case Mt:
              case Tt:
              case Ct:
                return n;
              default:
                return e;
            }
        }
      case dn:
        return e;
    }
  }
}
H.ContextConsumer = Et;
H.ContextProvider = Ct;
H.Element = un;
H.ForwardRef = _t;
H.Fragment = wt;
H.Lazy = Mt;
H.Memo = Tt;
H.Portal = dn;
H.Profiler = xt;
H.StrictMode = St;
H.Suspense = Rt;
H.SuspenseList = Pt;
H.isAsyncMode = function() {
  return !1;
};
H.isConcurrentMode = function() {
  return !1;
};
H.isContextConsumer = function(n) {
  return be(n) === Et;
};
H.isContextProvider = function(n) {
  return be(n) === Ct;
};
H.isElement = function(n) {
  return typeof n == "object" && n !== null && n.$$typeof === un;
};
H.isForwardRef = function(n) {
  return be(n) === _t;
};
H.isFragment = function(n) {
  return be(n) === wt;
};
H.isLazy = function(n) {
  return be(n) === Mt;
};
H.isMemo = function(n) {
  return be(n) === Tt;
};
H.isPortal = function(n) {
  return be(n) === dn;
};
H.isProfiler = function(n) {
  return be(n) === xt;
};
H.isStrictMode = function(n) {
  return be(n) === St;
};
H.isSuspense = function(n) {
  return be(n) === Rt;
};
H.isSuspenseList = function(n) {
  return be(n) === Pt;
};
H.isValidElementType = function(n) {
  return typeof n == "string" || typeof n == "function" || n === wt || n === xt || n === St || n === Rt || n === Pt || n === fs || typeof n == "object" && n !== null && (n.$$typeof === Mt || n.$$typeof === Tt || n.$$typeof === Ct || n.$$typeof === Et || n.$$typeof === _t || n.$$typeof === Er || n.getModuleId !== void 0);
};
H.typeOf = be;
Cr.exports = H;
var jt = Cr.exports, hs = Symbol.for("react.element"), ps = Symbol.for("react.transitional.element"), ms = Symbol.for("react.fragment");
function gs(n) {
  return (
    // Base object type
    n && _e(n) === "object" && // React Element type
    (n.$$typeof === hs || n.$$typeof === ps) && // React Fragment type
    n.type === ms
  );
}
var vs = Number(ii.split(".")[0]), bs = function(e, t) {
  typeof e == "function" ? e(t) : _e(e) === "object" && e && "current" in e && (e.current = t);
}, ys = function(e) {
  var t, r;
  if (!e)
    return !1;
  if (_r(e) && vs >= 19)
    return !0;
  var i = jt.isMemo(e) ? e.type.type : e.type;
  return !(typeof i == "function" && !((t = i.prototype) !== null && t !== void 0 && t.render) && i.$$typeof !== jt.ForwardRef || typeof e == "function" && !((r = e.prototype) !== null && r !== void 0 && r.render) && e.$$typeof !== jt.ForwardRef);
};
function _r(n) {
  return /* @__PURE__ */ oi(n) && !gs(n);
}
var ws = function(e) {
  if (e && _r(e)) {
    var t = e;
    return t.props.propertyIsEnumerable("ref") ? t.props.ref : t.ref;
  }
  return null;
};
function Ss(n, e) {
  for (var t = n, r = 0; r < e.length; r += 1) {
    if (t == null)
      return;
    t = t[e[r]];
  }
  return t;
}
function Dn(n, e, t, r) {
  var i = k({}, e[n]);
  if (r != null && r.deprecatedTokens) {
    var o = r.deprecatedTokens;
    o.forEach(function(a) {
      var c = ge(a, 2), l = c[0], u = c[1];
      if (i != null && i[l] || i != null && i[u]) {
        var d;
        (d = i[u]) !== null && d !== void 0 || (i[u] = i == null ? void 0 : i[l]);
      }
    });
  }
  var s = k(k({}, t), i);
  return Object.keys(s).forEach(function(a) {
    s[a] === e[a] && delete s[a];
  }), s;
}
var Rr = typeof CSSINJS_STATISTIC < "u", en = !0;
function Lt() {
  for (var n = arguments.length, e = new Array(n), t = 0; t < n; t++)
    e[t] = arguments[t];
  if (!Rr)
    return Object.assign.apply(Object, [{}].concat(e));
  en = !1;
  var r = {};
  return e.forEach(function(i) {
    if (fe(i) === "object") {
      var o = Object.keys(i);
      o.forEach(function(s) {
        Object.defineProperty(r, s, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return i[s];
          }
        });
      });
    }
  }), en = !0, r;
}
var Fn = {};
function xs() {
}
var Cs = function(e) {
  var t, r = e, i = xs;
  return Rr && typeof Proxy < "u" && (t = /* @__PURE__ */ new Set(), r = new Proxy(e, {
    get: function(s, a) {
      if (en) {
        var c;
        (c = t) === null || c === void 0 || c.add(a);
      }
      return s[a];
    }
  }), i = function(s, a) {
    var c;
    Fn[s] = {
      global: Array.from(t),
      component: k(k({}, (c = Fn[s]) === null || c === void 0 ? void 0 : c.component), a)
    };
  }), {
    token: r,
    keys: t,
    flush: i
  };
};
function Nn(n, e, t) {
  if (typeof t == "function") {
    var r;
    return t(Lt(e, (r = e[n]) !== null && r !== void 0 ? r : {}));
  }
  return t ?? {};
}
function Es(n) {
  return n === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var t = arguments.length, r = new Array(t), i = 0; i < t; i++)
        r[i] = arguments[i];
      return "max(".concat(r.map(function(o) {
        return Yt(o);
      }).join(","), ")");
    },
    min: function() {
      for (var t = arguments.length, r = new Array(t), i = 0; i < t; i++)
        r[i] = arguments[i];
      return "min(".concat(r.map(function(o) {
        return Yt(o);
      }).join(","), ")");
    }
  };
}
var _s = 1e3 * 60 * 10, Rs = /* @__PURE__ */ function() {
  function n() {
    De(this, n), D(this, "map", /* @__PURE__ */ new Map()), D(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), D(this, "nextID", 0), D(this, "lastAccessBeat", /* @__PURE__ */ new Map()), D(this, "accessBeat", 0);
  }
  return Fe(n, [{
    key: "set",
    value: function(t, r) {
      this.clear();
      var i = this.getCompositeKey(t);
      this.map.set(i, r), this.lastAccessBeat.set(i, Date.now());
    }
  }, {
    key: "get",
    value: function(t) {
      var r = this.getCompositeKey(t), i = this.map.get(r);
      return this.lastAccessBeat.set(r, Date.now()), this.accessBeat += 1, i;
    }
  }, {
    key: "getCompositeKey",
    value: function(t) {
      var r = this, i = t.map(function(o) {
        return o && fe(o) === "object" ? "obj_".concat(r.getObjectID(o)) : "".concat(fe(o), "_").concat(o);
      });
      return i.join("|");
    }
  }, {
    key: "getObjectID",
    value: function(t) {
      if (this.objectIDMap.has(t))
        return this.objectIDMap.get(t);
      var r = this.nextID;
      return this.objectIDMap.set(t, r), this.nextID += 1, r;
    }
  }, {
    key: "clear",
    value: function() {
      var t = this;
      if (this.accessBeat > 1e4) {
        var r = Date.now();
        this.lastAccessBeat.forEach(function(i, o) {
          r - i > _s && (t.map.delete(o), t.lastAccessBeat.delete(o));
        }), this.accessBeat = 0;
      }
    }
  }]), n;
}(), jn = new Rs();
function Ps(n, e) {
  return f.useMemo(function() {
    var t = jn.get(e);
    if (t)
      return t;
    var r = n();
    return jn.set(e, r), r;
  }, e);
}
var Ts = function() {
  return {};
};
function Ms(n) {
  var e = n.useCSP, t = e === void 0 ? Ts : e, r = n.useToken, i = n.usePrefix, o = n.getResetStyles, s = n.getCommonStyle, a = n.getCompUnitless;
  function c(h, p, v, g) {
    var m = Array.isArray(h) ? h[0] : h;
    function b(R) {
      return "".concat(String(m)).concat(R.slice(0, 1).toUpperCase()).concat(R.slice(1));
    }
    var w = (g == null ? void 0 : g.unitless) || {}, C = typeof a == "function" ? a(h) : {}, E = k(k({}, C), {}, D({}, b("zIndexPopup"), !0));
    Object.keys(w).forEach(function(R) {
      E[b(R)] = w[R];
    });
    var S = k(k({}, g), {}, {
      unitless: E,
      prefixToken: b
    }), x = u(h, p, v, S), T = l(m, v, S);
    return function(R) {
      var O = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : R, P = x(R, O), M = ge(P, 2), $ = M[1], N = T(O), W = ge(N, 2), A = W[0], U = W[1];
      return [A, $, U];
    };
  }
  function l(h, p, v) {
    var g = v.unitless, m = v.injectStyle, b = m === void 0 ? !0 : m, w = v.prefixToken, C = v.ignore, E = function(T) {
      var R = T.rootCls, O = T.cssVar, P = O === void 0 ? {} : O, M = r(), $ = M.realToken;
      return zi({
        path: [h],
        prefix: P.prefix,
        key: P.key,
        unitless: g,
        ignore: C,
        token: $,
        scope: R
      }, function() {
        var N = Nn(h, $, p), W = Dn(h, $, N, {
          deprecatedTokens: v == null ? void 0 : v.deprecatedTokens
        });
        return Object.keys(N).forEach(function(A) {
          W[w(A)] = W[A], delete W[A];
        }), W;
      }), null;
    }, S = function(T) {
      var R = r(), O = R.cssVar;
      return [function(P) {
        return b && O ? /* @__PURE__ */ f.createElement(f.Fragment, null, /* @__PURE__ */ f.createElement(E, {
          rootCls: T,
          cssVar: O,
          component: h
        }), P) : P;
      }, O == null ? void 0 : O.key];
    };
    return S;
  }
  function u(h, p, v) {
    var g = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, m = Array.isArray(h) ? h : [h, h], b = ge(m, 1), w = b[0], C = m.join("-"), E = n.layer || {
      name: "antd"
    };
    return function(S) {
      var x = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : S, T = r(), R = T.theme, O = T.realToken, P = T.hashId, M = T.token, $ = T.cssVar, N = i(), W = N.rootPrefixCls, A = N.iconPrefixCls, U = t(), F = $ ? "css" : "js", I = Ps(function() {
        var z = /* @__PURE__ */ new Set();
        return $ && Object.keys(g.unitless || {}).forEach(function(Q) {
          z.add($t(Q, $.prefix)), z.add($t(Q, An(w, $.prefix)));
        }), os(F, z);
      }, [F, w, $ == null ? void 0 : $.prefix]), y = Es(F), le = y.max, ee = y.min, J = {
        theme: R,
        token: M,
        hashId: P,
        nonce: function() {
          return U.nonce;
        },
        clientOnly: g.clientOnly,
        layer: E,
        // antd is always at top of styles
        order: g.order || -999
      };
      typeof o == "function" && gn(k(k({}, J), {}, {
        clientOnly: !1,
        path: ["Shared", W]
      }), function() {
        return o(M, {
          prefix: {
            rootPrefixCls: W,
            iconPrefixCls: A
          },
          csp: U
        });
      });
      var V = gn(k(k({}, J), {}, {
        path: [C, S, A]
      }), function() {
        if (g.injectStyle === !1)
          return [];
        var z = Cs(M), Q = z.token, te = z.flush, ce = Nn(w, O, v), Se = ".".concat(S), B = Dn(w, O, ce, {
          deprecatedTokens: g.deprecatedTokens
        });
        $ && ce && fe(ce) === "object" && Object.keys(ce).forEach(function(Y) {
          ce[Y] = "var(".concat($t(Y, An(w, $.prefix)), ")");
        });
        var L = Lt(Q, {
          componentCls: Se,
          prefixCls: S,
          iconCls: ".".concat(A),
          antCls: ".".concat(W),
          calc: I,
          // @ts-ignore
          max: le,
          // @ts-ignore
          min: ee
        }, $ ? ce : B), j = p(L, {
          hashId: P,
          prefixCls: S,
          rootPrefixCls: W,
          iconPrefixCls: A
        });
        te(w, B);
        var ne = typeof s == "function" ? s(L, S, x, g.resetFont) : null;
        return [g.resetStyle === !1 ? null : ne, j];
      });
      return [V, P];
    };
  }
  function d(h, p, v) {
    var g = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, m = u(h, p, v, k({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, g)), b = function(C) {
      var E = C.prefixCls, S = C.rootCls, x = S === void 0 ? E : S;
      return m(E, x), null;
    };
    return b;
  }
  return {
    genStyleHooks: c,
    genSubStyleComponent: d,
    genComponentStyleHook: u
  };
}
const Ls = {
  blue: "#1677FF",
  purple: "#722ED1",
  cyan: "#13C2C2",
  green: "#52C41A",
  magenta: "#EB2F96",
  /**
   * @deprecated Use magenta instead
   */
  pink: "#EB2F96",
  red: "#F5222D",
  orange: "#FA8C16",
  yellow: "#FADB14",
  volcano: "#FA541C",
  geekblue: "#2F54EB",
  gold: "#FAAD14",
  lime: "#A0D911"
}, Os = Object.assign(Object.assign({}, Ls), {
  // Color
  colorPrimary: "#1677ff",
  colorSuccess: "#52c41a",
  colorWarning: "#faad14",
  colorError: "#ff4d4f",
  colorInfo: "#1677ff",
  colorLink: "",
  colorTextBase: "",
  colorBgBase: "",
  // Font
  fontFamily: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
'Noto Color Emoji'`,
  fontFamilyCode: "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace",
  fontSize: 14,
  // Line
  lineWidth: 1,
  lineType: "solid",
  // Motion
  motionUnit: 0.1,
  motionBase: 0,
  motionEaseOutCirc: "cubic-bezier(0.08, 0.82, 0.17, 1)",
  motionEaseInOutCirc: "cubic-bezier(0.78, 0.14, 0.15, 0.86)",
  motionEaseOut: "cubic-bezier(0.215, 0.61, 0.355, 1)",
  motionEaseInOut: "cubic-bezier(0.645, 0.045, 0.355, 1)",
  motionEaseOutBack: "cubic-bezier(0.12, 0.4, 0.29, 1.46)",
  motionEaseInBack: "cubic-bezier(0.71, -0.46, 0.88, 0.6)",
  motionEaseInQuint: "cubic-bezier(0.755, 0.05, 0.855, 0.06)",
  motionEaseOutQuint: "cubic-bezier(0.23, 1, 0.32, 1)",
  // Radius
  borderRadius: 6,
  // Size
  sizeUnit: 4,
  sizeStep: 4,
  sizePopupArrow: 16,
  // Control Base
  controlHeight: 32,
  // zIndex
  zIndexBase: 0,
  zIndexPopupBase: 1e3,
  // Image
  opacityImage: 1,
  // Wireframe
  wireframe: !1,
  // Motion
  motion: !0
}), ae = Math.round;
function Wt(n, e) {
  const t = n.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], r = t.map((i) => parseFloat(i));
  for (let i = 0; i < 3; i += 1)
    r[i] = e(r[i] || 0, t[i] || "", i);
  return t[3] ? r[3] = t[3].includes("%") ? r[3] / 100 : r[3] : r[3] = 1, r;
}
const Wn = (n, e, t) => t === 0 ? n : n / 100;
function We(n, e) {
  const t = e || 255;
  return n > t ? t : n < 0 ? 0 : n;
}
class xe {
  constructor(e) {
    D(this, "isValid", !0), D(this, "r", 0), D(this, "g", 0), D(this, "b", 0), D(this, "a", 1), D(this, "_h", void 0), D(this, "_s", void 0), D(this, "_l", void 0), D(this, "_v", void 0), D(this, "_max", void 0), D(this, "_min", void 0), D(this, "_brightness", void 0);
    function t(r) {
      return r[0] in e && r[1] in e && r[2] in e;
    }
    if (e) if (typeof e == "string") {
      let i = function(o) {
        return r.startsWith(o);
      };
      const r = e.trim();
      /^#?[A-F\d]{3,8}$/i.test(r) ? this.fromHexString(r) : i("rgb") ? this.fromRgbString(r) : i("hsl") ? this.fromHslString(r) : (i("hsv") || i("hsb")) && this.fromHsvString(r);
    } else if (e instanceof xe)
      this.r = e.r, this.g = e.g, this.b = e.b, this.a = e.a, this._h = e._h, this._s = e._s, this._l = e._l, this._v = e._v;
    else if (t("rgb"))
      this.r = We(e.r), this.g = We(e.g), this.b = We(e.b), this.a = typeof e.a == "number" ? We(e.a, 1) : 1;
    else if (t("hsl"))
      this.fromHsl(e);
    else if (t("hsv"))
      this.fromHsv(e);
    else
      throw new Error("@ant-design/fast-color: unsupported input " + JSON.stringify(e));
  }
  // ======================= Setter =======================
  setR(e) {
    return this._sc("r", e);
  }
  setG(e) {
    return this._sc("g", e);
  }
  setB(e) {
    return this._sc("b", e);
  }
  setA(e) {
    return this._sc("a", e, 1);
  }
  setHue(e) {
    const t = this.toHsv();
    return t.h = e, this._c(t);
  }
  // ======================= Getter =======================
  /**
   * Returns the perceived luminance of a color, from 0-1.
   * @see http://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef
   */
  getLuminance() {
    function e(o) {
      const s = o / 255;
      return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
    }
    const t = e(this.r), r = e(this.g), i = e(this.b);
    return 0.2126 * t + 0.7152 * r + 0.0722 * i;
  }
  getHue() {
    if (typeof this._h > "u") {
      const e = this.getMax() - this.getMin();
      e === 0 ? this._h = 0 : this._h = ae(60 * (this.r === this.getMax() ? (this.g - this.b) / e + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / e + 2 : (this.r - this.g) / e + 4));
    }
    return this._h;
  }
  getSaturation() {
    if (typeof this._s > "u") {
      const e = this.getMax() - this.getMin();
      e === 0 ? this._s = 0 : this._s = e / this.getMax();
    }
    return this._s;
  }
  getLightness() {
    return typeof this._l > "u" && (this._l = (this.getMax() + this.getMin()) / 510), this._l;
  }
  getValue() {
    return typeof this._v > "u" && (this._v = this.getMax() / 255), this._v;
  }
  /**
   * Returns the perceived brightness of the color, from 0-255.
   * Note: this is not the b of HSB
   * @see http://www.w3.org/TR/AERT#color-contrast
   */
  getBrightness() {
    return typeof this._brightness > "u" && (this._brightness = (this.r * 299 + this.g * 587 + this.b * 114) / 1e3), this._brightness;
  }
  // ======================== Func ========================
  darken(e = 10) {
    const t = this.getHue(), r = this.getSaturation();
    let i = this.getLightness() - e / 100;
    return i < 0 && (i = 0), this._c({
      h: t,
      s: r,
      l: i,
      a: this.a
    });
  }
  lighten(e = 10) {
    const t = this.getHue(), r = this.getSaturation();
    let i = this.getLightness() + e / 100;
    return i > 1 && (i = 1), this._c({
      h: t,
      s: r,
      l: i,
      a: this.a
    });
  }
  /**
   * Mix the current color a given amount with another color, from 0 to 100.
   * 0 means no mixing (return current color).
   */
  mix(e, t = 50) {
    const r = this._c(e), i = t / 100, o = (a) => (r[a] - this[a]) * i + this[a], s = {
      r: ae(o("r")),
      g: ae(o("g")),
      b: ae(o("b")),
      a: ae(o("a") * 100) / 100
    };
    return this._c(s);
  }
  /**
   * Mix the color with pure white, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return white.
   */
  tint(e = 10) {
    return this.mix({
      r: 255,
      g: 255,
      b: 255,
      a: 1
    }, e);
  }
  /**
   * Mix the color with pure black, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return black.
   */
  shade(e = 10) {
    return this.mix({
      r: 0,
      g: 0,
      b: 0,
      a: 1
    }, e);
  }
  onBackground(e) {
    const t = this._c(e), r = this.a + t.a * (1 - this.a), i = (o) => ae((this[o] * this.a + t[o] * t.a * (1 - this.a)) / r);
    return this._c({
      r: i("r"),
      g: i("g"),
      b: i("b"),
      a: r
    });
  }
  // ======================= Status =======================
  isDark() {
    return this.getBrightness() < 128;
  }
  isLight() {
    return this.getBrightness() >= 128;
  }
  // ======================== MISC ========================
  equals(e) {
    return this.r === e.r && this.g === e.g && this.b === e.b && this.a === e.a;
  }
  clone() {
    return this._c(this);
  }
  // ======================= Format =======================
  toHexString() {
    let e = "#";
    const t = (this.r || 0).toString(16);
    e += t.length === 2 ? t : "0" + t;
    const r = (this.g || 0).toString(16);
    e += r.length === 2 ? r : "0" + r;
    const i = (this.b || 0).toString(16);
    if (e += i.length === 2 ? i : "0" + i, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const o = ae(this.a * 255).toString(16);
      e += o.length === 2 ? o : "0" + o;
    }
    return e;
  }
  /** CSS support color pattern */
  toHsl() {
    return {
      h: this.getHue(),
      s: this.getSaturation(),
      l: this.getLightness(),
      a: this.a
    };
  }
  /** CSS support color pattern */
  toHslString() {
    const e = this.getHue(), t = ae(this.getSaturation() * 100), r = ae(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${e},${t}%,${r}%,${this.a})` : `hsl(${e},${t}%,${r}%)`;
  }
  /** Same as toHsb */
  toHsv() {
    return {
      h: this.getHue(),
      s: this.getSaturation(),
      v: this.getValue(),
      a: this.a
    };
  }
  toRgb() {
    return {
      r: this.r,
      g: this.g,
      b: this.b,
      a: this.a
    };
  }
  toRgbString() {
    return this.a !== 1 ? `rgba(${this.r},${this.g},${this.b},${this.a})` : `rgb(${this.r},${this.g},${this.b})`;
  }
  toString() {
    return this.toRgbString();
  }
  // ====================== Privates ======================
  /** Return a new FastColor object with one channel changed */
  _sc(e, t, r) {
    const i = this.clone();
    return i[e] = We(t, r), i;
  }
  _c(e) {
    return new this.constructor(e);
  }
  getMax() {
    return typeof this._max > "u" && (this._max = Math.max(this.r, this.g, this.b)), this._max;
  }
  getMin() {
    return typeof this._min > "u" && (this._min = Math.min(this.r, this.g, this.b)), this._min;
  }
  fromHexString(e) {
    const t = e.replace("#", "");
    function r(i, o) {
      return parseInt(t[i] + t[o || i], 16);
    }
    t.length < 6 ? (this.r = r(0), this.g = r(1), this.b = r(2), this.a = t[3] ? r(3) / 255 : 1) : (this.r = r(0, 1), this.g = r(2, 3), this.b = r(4, 5), this.a = t[6] ? r(6, 7) / 255 : 1);
  }
  fromHsl({
    h: e,
    s: t,
    l: r,
    a: i
  }) {
    if (this._h = e % 360, this._s = t, this._l = r, this.a = typeof i == "number" ? i : 1, t <= 0) {
      const h = ae(r * 255);
      this.r = h, this.g = h, this.b = h;
    }
    let o = 0, s = 0, a = 0;
    const c = e / 60, l = (1 - Math.abs(2 * r - 1)) * t, u = l * (1 - Math.abs(c % 2 - 1));
    c >= 0 && c < 1 ? (o = l, s = u) : c >= 1 && c < 2 ? (o = u, s = l) : c >= 2 && c < 3 ? (s = l, a = u) : c >= 3 && c < 4 ? (s = u, a = l) : c >= 4 && c < 5 ? (o = u, a = l) : c >= 5 && c < 6 && (o = l, a = u);
    const d = r - l / 2;
    this.r = ae((o + d) * 255), this.g = ae((s + d) * 255), this.b = ae((a + d) * 255);
  }
  fromHsv({
    h: e,
    s: t,
    v: r,
    a: i
  }) {
    this._h = e % 360, this._s = t, this._v = r, this.a = typeof i == "number" ? i : 1;
    const o = ae(r * 255);
    if (this.r = o, this.g = o, this.b = o, t <= 0)
      return;
    const s = e / 60, a = Math.floor(s), c = s - a, l = ae(r * (1 - t) * 255), u = ae(r * (1 - t * c) * 255), d = ae(r * (1 - t * (1 - c)) * 255);
    switch (a) {
      case 0:
        this.g = d, this.b = l;
        break;
      case 1:
        this.r = u, this.b = l;
        break;
      case 2:
        this.r = l, this.b = d;
        break;
      case 3:
        this.r = l, this.g = u;
        break;
      case 4:
        this.r = d, this.g = l;
        break;
      case 5:
      default:
        this.g = l, this.b = u;
        break;
    }
  }
  fromHsvString(e) {
    const t = Wt(e, Wn);
    this.fromHsv({
      h: t[0],
      s: t[1],
      v: t[2],
      a: t[3]
    });
  }
  fromHslString(e) {
    const t = Wt(e, Wn);
    this.fromHsl({
      h: t[0],
      s: t[1],
      l: t[2],
      a: t[3]
    });
  }
  fromRgbString(e) {
    const t = Wt(e, (r, i) => (
      // Convert percentage to number. e.g. 50% -> 128
      i.includes("%") ? ae(r / 100 * 255) : r
    ));
    this.r = t[0], this.g = t[1], this.b = t[2], this.a = t[3];
  }
}
function Bt(n) {
  return n >= 0 && n <= 255;
}
function Ke(n, e) {
  const {
    r: t,
    g: r,
    b: i,
    a: o
  } = new xe(n).toRgb();
  if (o < 1)
    return n;
  const {
    r: s,
    g: a,
    b: c
  } = new xe(e).toRgb();
  for (let l = 0.01; l <= 1; l += 0.01) {
    const u = Math.round((t - s * (1 - l)) / l), d = Math.round((r - a * (1 - l)) / l), h = Math.round((i - c * (1 - l)) / l);
    if (Bt(u) && Bt(d) && Bt(h))
      return new xe({
        r: u,
        g: d,
        b: h,
        a: Math.round(l * 100) / 100
      }).toRgbString();
  }
  return new xe({
    r: t,
    g: r,
    b: i,
    a: 1
  }).toRgbString();
}
var As = function(n, e) {
  var t = {};
  for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && e.indexOf(r) < 0 && (t[r] = n[r]);
  if (n != null && typeof Object.getOwnPropertySymbols == "function") for (var i = 0, r = Object.getOwnPropertySymbols(n); i < r.length; i++)
    e.indexOf(r[i]) < 0 && Object.prototype.propertyIsEnumerable.call(n, r[i]) && (t[r[i]] = n[r[i]]);
  return t;
};
function Is(n) {
  const {
    override: e
  } = n, t = As(n, ["override"]), r = Object.assign({}, e);
  Object.keys(Os).forEach((h) => {
    delete r[h];
  });
  const i = Object.assign(Object.assign({}, t), r), o = 480, s = 576, a = 768, c = 992, l = 1200, u = 1600;
  if (i.motion === !1) {
    const h = "0s";
    i.motionDurationFast = h, i.motionDurationMid = h, i.motionDurationSlow = h;
  }
  return Object.assign(Object.assign(Object.assign({}, i), {
    // ============== Background ============== //
    colorFillContent: i.colorFillSecondary,
    colorFillContentHover: i.colorFill,
    colorFillAlter: i.colorFillQuaternary,
    colorBgContainerDisabled: i.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: i.colorBgContainer,
    colorSplit: Ke(i.colorBorderSecondary, i.colorBgContainer),
    // ============== Text ============== //
    colorTextPlaceholder: i.colorTextQuaternary,
    colorTextDisabled: i.colorTextQuaternary,
    colorTextHeading: i.colorText,
    colorTextLabel: i.colorTextSecondary,
    colorTextDescription: i.colorTextTertiary,
    colorTextLightSolid: i.colorWhite,
    colorHighlight: i.colorError,
    colorBgTextHover: i.colorFillSecondary,
    colorBgTextActive: i.colorFill,
    colorIcon: i.colorTextTertiary,
    colorIconHover: i.colorText,
    colorErrorOutline: Ke(i.colorErrorBg, i.colorBgContainer),
    colorWarningOutline: Ke(i.colorWarningBg, i.colorBgContainer),
    // Font
    fontSizeIcon: i.fontSizeSM,
    // Line
    lineWidthFocus: i.lineWidth * 3,
    // Control
    lineWidth: i.lineWidth,
    controlOutlineWidth: i.lineWidth * 2,
    // Checkbox size and expand icon size
    controlInteractiveSize: i.controlHeight / 2,
    controlItemBgHover: i.colorFillTertiary,
    controlItemBgActive: i.colorPrimaryBg,
    controlItemBgActiveHover: i.colorPrimaryBgHover,
    controlItemBgActiveDisabled: i.colorFill,
    controlTmpOutline: i.colorFillQuaternary,
    controlOutline: Ke(i.colorPrimaryBg, i.colorBgContainer),
    lineType: i.lineType,
    borderRadius: i.borderRadius,
    borderRadiusXS: i.borderRadiusXS,
    borderRadiusSM: i.borderRadiusSM,
    borderRadiusLG: i.borderRadiusLG,
    fontWeightStrong: 600,
    opacityLoading: 0.65,
    linkDecoration: "none",
    linkHoverDecoration: "none",
    linkFocusDecoration: "none",
    controlPaddingHorizontal: 12,
    controlPaddingHorizontalSM: 8,
    paddingXXS: i.sizeXXS,
    paddingXS: i.sizeXS,
    paddingSM: i.sizeSM,
    padding: i.size,
    paddingMD: i.sizeMD,
    paddingLG: i.sizeLG,
    paddingXL: i.sizeXL,
    paddingContentHorizontalLG: i.sizeLG,
    paddingContentVerticalLG: i.sizeMS,
    paddingContentHorizontal: i.sizeMS,
    paddingContentVertical: i.sizeSM,
    paddingContentHorizontalSM: i.size,
    paddingContentVerticalSM: i.sizeXS,
    marginXXS: i.sizeXXS,
    marginXS: i.sizeXS,
    marginSM: i.sizeSM,
    margin: i.size,
    marginMD: i.sizeMD,
    marginLG: i.sizeLG,
    marginXL: i.sizeXL,
    marginXXL: i.sizeXXL,
    boxShadow: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowSecondary: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowTertiary: `
      0 1px 2px 0 rgba(0, 0, 0, 0.03),
      0 1px 6px -1px rgba(0, 0, 0, 0.02),
      0 2px 4px 0 rgba(0, 0, 0, 0.02)
    `,
    screenXS: o,
    screenXSMin: o,
    screenXSMax: s - 1,
    screenSM: s,
    screenSMMin: s,
    screenSMMax: a - 1,
    screenMD: a,
    screenMDMin: a,
    screenMDMax: c - 1,
    screenLG: c,
    screenLGMin: c,
    screenLGMax: l - 1,
    screenXL: l,
    screenXLMin: l,
    screenXLMax: u - 1,
    screenXXL: u,
    screenXXLMin: u,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new xe("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new xe("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new xe("rgba(0, 0, 0, 0.09)").toRgbString()}
    `,
    boxShadowDrawerRight: `
      -6px 0 16px 0 rgba(0, 0, 0, 0.08),
      -3px 0 6px -4px rgba(0, 0, 0, 0.12),
      -9px 0 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerLeft: `
      6px 0 16px 0 rgba(0, 0, 0, 0.08),
      3px 0 6px -4px rgba(0, 0, 0, 0.12),
      9px 0 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerUp: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerDown: `
      0 -6px 16px 0 rgba(0, 0, 0, 0.08),
      0 -3px 6px -4px rgba(0, 0, 0, 0.12),
      0 -9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowTabsOverflowLeft: "inset 10px 0 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowRight: "inset -10px 0 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowTop: "inset 0 10px 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowBottom: "inset 0 -10px 8px -8px rgba(0, 0, 0, 0.08)"
  }), r);
}
const $s = {
  lineHeight: !0,
  lineHeightSM: !0,
  lineHeightLG: !0,
  lineHeightHeading1: !0,
  lineHeightHeading2: !0,
  lineHeightHeading3: !0,
  lineHeightHeading4: !0,
  lineHeightHeading5: !0,
  opacityLoading: !0,
  fontWeightStrong: !0,
  zIndexPopupBase: !0,
  zIndexBase: !0,
  opacityImage: !0
}, ks = {
  motionBase: !0,
  motionUnit: !0
}, Ds = Ui(dt.defaultAlgorithm), Fs = {
  screenXS: !0,
  screenXSMin: !0,
  screenXSMax: !0,
  screenSM: !0,
  screenSMMin: !0,
  screenSMMax: !0,
  screenMD: !0,
  screenMDMin: !0,
  screenMDMax: !0,
  screenLG: !0,
  screenLGMin: !0,
  screenLGMax: !0,
  screenXL: !0,
  screenXLMin: !0,
  screenXLMax: !0,
  screenXXL: !0,
  screenXXLMin: !0
}, Pr = (n, e, t) => {
  const r = t.getDerivativeToken(n), {
    override: i,
    ...o
  } = e;
  let s = {
    ...r,
    override: i
  };
  return s = Is(s), o && Object.entries(o).forEach(([a, c]) => {
    const {
      theme: l,
      ...u
    } = c;
    let d = u;
    l && (d = Pr({
      ...s,
      ...u
    }, {
      override: u
    }, l)), s[a] = d;
  }), s;
};
function Ns() {
  const {
    token: n,
    hashed: e,
    theme: t = Ds,
    override: r,
    cssVar: i
  } = f.useContext(dt._internalContext), [o, s, a] = Vi(t, [dt.defaultSeed, n], {
    salt: `${Fo}-${e || ""}`,
    override: r,
    getComputedToken: Pr,
    cssVar: i && {
      prefix: i.prefix,
      key: i.key,
      unitless: $s,
      ignore: ks,
      preserve: Fs
    }
  });
  return [t, a, e ? s : "", o, i];
}
const {
  genStyleHooks: Tr
} = Ms({
  usePrefix: () => {
    const {
      getPrefixCls: n,
      iconPrefixCls: e
    } = Ue();
    return {
      iconPrefixCls: e,
      rootPrefixCls: n()
    };
  },
  useToken: () => {
    const [n, e, t, r, i] = Ns();
    return {
      theme: n,
      realToken: e,
      hashId: t,
      token: r,
      cssVar: i
    };
  },
  useCSP: () => {
    const {
      csp: n
    } = Ue();
    return n ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), Xe = /* @__PURE__ */ f.createContext(null);
function Bn(n) {
  const {
    getDropContainer: e,
    className: t,
    prefixCls: r,
    children: i
  } = n, {
    disabled: o
  } = f.useContext(Xe), [s, a] = f.useState(), [c, l] = f.useState(null);
  if (f.useEffect(() => {
    const h = e == null ? void 0 : e();
    s !== h && a(h);
  }, [e]), f.useEffect(() => {
    if (s) {
      const h = () => {
        l(!0);
      }, p = (m) => {
        m.preventDefault();
      }, v = (m) => {
        m.relatedTarget || l(!1);
      }, g = (m) => {
        l(!1), m.preventDefault();
      };
      return document.addEventListener("dragenter", h), document.addEventListener("dragover", p), document.addEventListener("dragleave", v), document.addEventListener("drop", g), () => {
        document.removeEventListener("dragenter", h), document.removeEventListener("dragover", p), document.removeEventListener("dragleave", v), document.removeEventListener("drop", g);
      };
    }
  }, [!!s]), !(e && s && !o))
    return null;
  const d = `${r}-drop-area`;
  return /* @__PURE__ */ ut(/* @__PURE__ */ f.createElement("div", {
    className: K(d, t, {
      [`${d}-on-body`]: s.tagName === "BODY"
    }),
    style: {
      display: c ? "block" : "none"
    }
  }, i), s);
}
function Hn(n) {
  return n instanceof HTMLElement || n instanceof SVGElement;
}
function js(n) {
  return n && _e(n) === "object" && Hn(n.nativeElement) ? n.nativeElement : Hn(n) ? n : null;
}
function Ws(n) {
  var e = js(n);
  if (e)
    return e;
  if (n instanceof f.Component) {
    var t;
    return (t = mn.findDOMNode) === null || t === void 0 ? void 0 : t.call(mn, n);
  }
  return null;
}
function Bs(n, e) {
  if (n == null) return {};
  var t = {};
  for (var r in n) if ({}.hasOwnProperty.call(n, r)) {
    if (e.indexOf(r) !== -1) continue;
    t[r] = n[r];
  }
  return t;
}
function zn(n, e) {
  if (n == null) return {};
  var t, r, i = Bs(n, e);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(n);
    for (r = 0; r < o.length; r++) t = o[r], e.indexOf(t) === -1 && {}.propertyIsEnumerable.call(n, t) && (i[t] = n[t]);
  }
  return i;
}
var Hs = /* @__PURE__ */ _.createContext({}), zs = /* @__PURE__ */ function(n) {
  vt(t, n);
  var e = bt(t);
  function t() {
    return De(this, t), e.apply(this, arguments);
  }
  return Fe(t, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), t;
}(_.Component);
function Us(n) {
  var e = _.useReducer(function(a) {
    return a + 1;
  }, 0), t = pt(e, 2), r = t[1], i = _.useRef(n), o = Re(function() {
    return i.current;
  }), s = Re(function(a) {
    i.current = typeof a == "function" ? a(i.current) : a, r();
  });
  return [o, s];
}
var Ee = "none", Ye = "appear", Ze = "enter", Qe = "leave", Un = "none", we = "prepare", Ae = "start", Ie = "active", fn = "end", Mr = "prepared";
function Vn(n, e) {
  var t = {};
  return t[n.toLowerCase()] = e.toLowerCase(), t["Webkit".concat(n)] = "webkit".concat(e), t["Moz".concat(n)] = "moz".concat(e), t["ms".concat(n)] = "MS".concat(e), t["O".concat(n)] = "o".concat(e.toLowerCase()), t;
}
function Vs(n, e) {
  var t = {
    animationend: Vn("Animation", "AnimationEnd"),
    transitionend: Vn("Transition", "TransitionEnd")
  };
  return n && ("AnimationEvent" in e || delete t.animationend.animation, "TransitionEvent" in e || delete t.transitionend.transition), t;
}
var Xs = Vs(yt(), typeof window < "u" ? window : {}), Lr = {};
if (yt()) {
  var Gs = document.createElement("div");
  Lr = Gs.style;
}
var Je = {};
function Or(n) {
  if (Je[n])
    return Je[n];
  var e = Xs[n];
  if (e)
    for (var t = Object.keys(e), r = t.length, i = 0; i < r; i += 1) {
      var o = t[i];
      if (Object.prototype.hasOwnProperty.call(e, o) && o in Lr)
        return Je[n] = e[o], Je[n];
    }
  return "";
}
var Ar = Or("animationend"), Ir = Or("transitionend"), $r = !!(Ar && Ir), Xn = Ar || "animationend", Gn = Ir || "transitionend";
function qn(n, e) {
  if (!n) return null;
  if (fe(n) === "object") {
    var t = e.replace(/-\w/g, function(r) {
      return r[1].toUpperCase();
    });
    return n[t];
  }
  return "".concat(n, "-").concat(e);
}
const qs = function(n) {
  var e = he();
  function t(i) {
    i && (i.removeEventListener(Gn, n), i.removeEventListener(Xn, n));
  }
  function r(i) {
    e.current && e.current !== i && t(e.current), i && i !== e.current && (i.addEventListener(Gn, n), i.addEventListener(Xn, n), e.current = i);
  }
  return _.useEffect(function() {
    return function() {
      t(e.current);
    };
  }, []), [r, t];
};
var kr = yt() ? si : Ce, Dr = function(e) {
  return +setTimeout(e, 16);
}, Fr = function(e) {
  return clearTimeout(e);
};
typeof window < "u" && "requestAnimationFrame" in window && (Dr = function(e) {
  return window.requestAnimationFrame(e);
}, Fr = function(e) {
  return window.cancelAnimationFrame(e);
});
var Kn = 0, hn = /* @__PURE__ */ new Map();
function Nr(n) {
  hn.delete(n);
}
var tn = function(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  Kn += 1;
  var r = Kn;
  function i(o) {
    if (o === 0)
      Nr(r), e();
    else {
      var s = Dr(function() {
        i(o - 1);
      });
      hn.set(r, s);
    }
  }
  return i(t), r;
};
tn.cancel = function(n) {
  var e = hn.get(n);
  return Nr(n), Fr(e);
};
const Ks = function() {
  var n = _.useRef(null);
  function e() {
    tn.cancel(n.current);
  }
  function t(r) {
    var i = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    e();
    var o = tn(function() {
      i <= 1 ? r({
        isCanceled: function() {
          return o !== n.current;
        }
      }) : t(r, i - 1);
    });
    n.current = o;
  }
  return _.useEffect(function() {
    return function() {
      e();
    };
  }, []), [t, e];
};
var Ys = [we, Ae, Ie, fn], Zs = [we, Mr], jr = !1, Qs = !0;
function Wr(n) {
  return n === Ie || n === fn;
}
const Js = function(n, e, t) {
  var r = Ve(Un), i = ge(r, 2), o = i[0], s = i[1], a = Ks(), c = ge(a, 2), l = c[0], u = c[1];
  function d() {
    s(we, !0);
  }
  var h = e ? Zs : Ys;
  return kr(function() {
    if (o !== Un && o !== fn) {
      var p = h.indexOf(o), v = h[p + 1], g = t(o);
      g === jr ? s(v, !0) : v && l(function(m) {
        function b() {
          m.isCanceled() || s(v, !0);
        }
        g === !0 ? b() : Promise.resolve(g).then(b);
      });
    }
  }, [n, o]), _.useEffect(function() {
    return function() {
      u();
    };
  }, []), [d, o];
};
function ea(n, e, t, r) {
  var i = r.motionEnter, o = i === void 0 ? !0 : i, s = r.motionAppear, a = s === void 0 ? !0 : s, c = r.motionLeave, l = c === void 0 ? !0 : c, u = r.motionDeadline, d = r.motionLeaveImmediately, h = r.onAppearPrepare, p = r.onEnterPrepare, v = r.onLeavePrepare, g = r.onAppearStart, m = r.onEnterStart, b = r.onLeaveStart, w = r.onAppearActive, C = r.onEnterActive, E = r.onLeaveActive, S = r.onAppearEnd, x = r.onEnterEnd, T = r.onLeaveEnd, R = r.onVisibleChanged, O = Ve(), P = ge(O, 2), M = P[0], $ = P[1], N = Us(Ee), W = ge(N, 2), A = W[0], U = W[1], F = Ve(null), I = ge(F, 2), y = I[0], le = I[1], ee = A(), J = he(!1), V = he(null);
  function z() {
    return t();
  }
  var Q = he(!1);
  function te() {
    U(Ee), le(null, !0);
  }
  var ce = Re(function(ie) {
    var oe = A();
    if (oe !== Ee) {
      var ue = z();
      if (!(ie && !ie.deadline && ie.target !== ue)) {
        var Me = Q.current, Pe;
        oe === Ye && Me ? Pe = S == null ? void 0 : S(ue, ie) : oe === Ze && Me ? Pe = x == null ? void 0 : x(ue, ie) : oe === Qe && Me && (Pe = T == null ? void 0 : T(ue, ie)), Me && Pe !== !1 && te();
      }
    }
  }), Se = qs(ce), B = ge(Se, 1), L = B[0], j = function(oe) {
    switch (oe) {
      case Ye:
        return D(D(D({}, we, h), Ae, g), Ie, w);
      case Ze:
        return D(D(D({}, we, p), Ae, m), Ie, C);
      case Qe:
        return D(D(D({}, we, v), Ae, b), Ie, E);
      default:
        return {};
    }
  }, ne = _.useMemo(function() {
    return j(ee);
  }, [ee]), Y = Js(ee, !n, function(ie) {
    if (ie === we) {
      var oe = ne[we];
      return oe ? oe(z()) : jr;
    }
    if (se in ne) {
      var ue;
      le(((ue = ne[se]) === null || ue === void 0 ? void 0 : ue.call(ne, z(), null)) || null);
    }
    return se === Ie && ee !== Ee && (L(z()), u > 0 && (clearTimeout(V.current), V.current = setTimeout(function() {
      ce({
        deadline: !0
      });
    }, u))), se === Mr && te(), Qs;
  }), re = ge(Y, 2), pe = re[0], se = re[1], X = Wr(se);
  Q.current = X;
  var me = he(null);
  kr(function() {
    if (!(J.current && me.current === e)) {
      $(e);
      var ie = J.current;
      J.current = !0;
      var oe;
      !ie && e && a && (oe = Ye), ie && e && o && (oe = Ze), (ie && !e && l || !ie && d && !e && l) && (oe = Qe);
      var ue = j(oe);
      oe && (n || ue[we]) ? (U(oe), pe()) : U(Ee), me.current = e;
    }
  }, [e]), Ce(function() {
    // Cancel appear
    (ee === Ye && !a || // Cancel enter
    ee === Ze && !o || // Cancel leave
    ee === Qe && !l) && U(Ee);
  }, [a, o, l]), Ce(function() {
    return function() {
      J.current = !1, clearTimeout(V.current);
    };
  }, []);
  var ye = _.useRef(!1);
  Ce(function() {
    M && (ye.current = !0), M !== void 0 && ee === Ee && ((ye.current || M) && (R == null || R(M)), ye.current = !0);
  }, [M, ee]);
  var G = y;
  return ne[we] && se === Ae && (G = k({
    transition: "none"
  }, G)), [ee, se, G, M ?? e];
}
function ta(n) {
  var e = n;
  fe(n) === "object" && (e = n.transitionSupport);
  function t(i, o) {
    return !!(i.motionName && e && o !== !1);
  }
  var r = /* @__PURE__ */ _.forwardRef(function(i, o) {
    var s = i.visible, a = s === void 0 ? !0 : s, c = i.removeOnLeave, l = c === void 0 ? !0 : c, u = i.forceRender, d = i.children, h = i.motionName, p = i.leavedClassName, v = i.eventProps, g = _.useContext(Hs), m = g.motion, b = t(i, m), w = he(), C = he();
    function E() {
      try {
        return w.current instanceof HTMLElement ? w.current : Ws(C.current);
      } catch {
        return null;
      }
    }
    var S = ea(b, a, E, i), x = ge(S, 4), T = x[0], R = x[1], O = x[2], P = x[3], M = _.useRef(P);
    P && (M.current = !0);
    var $ = _.useCallback(function(I) {
      w.current = I, bs(o, I);
    }, [o]), N, W = k(k({}, v), {}, {
      visible: a
    });
    if (!d)
      N = null;
    else if (T === Ee)
      P ? N = d(k({}, W), $) : !l && M.current && p ? N = d(k(k({}, W), {}, {
        className: p
      }), $) : u || !l && !p ? N = d(k(k({}, W), {}, {
        style: {
          display: "none"
        }
      }), $) : N = null;
    else {
      var A;
      R === we ? A = "prepare" : Wr(R) ? A = "active" : R === Ae && (A = "start");
      var U = qn(h, "".concat(T, "-").concat(A));
      N = d(k(k({}, W), {}, {
        className: K(qn(h, T), D(D({}, U, U && A), h, typeof h == "string")),
        style: O
      }), $);
    }
    if (/* @__PURE__ */ _.isValidElement(N) && ys(N)) {
      var F = ws(N);
      F || (N = /* @__PURE__ */ _.cloneElement(N, {
        ref: $
      }));
    }
    return /* @__PURE__ */ _.createElement(zs, {
      ref: C
    }, N);
  });
  return r.displayName = "CSSMotion", r;
}
const Br = ta($r);
var nn = "add", rn = "keep", on = "remove", Ht = "removed";
function na(n) {
  var e;
  return n && fe(n) === "object" && "key" in n ? e = n : e = {
    key: n
  }, k(k({}, e), {}, {
    key: String(e.key)
  });
}
function sn() {
  var n = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return n.map(na);
}
function ra() {
  var n = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], t = [], r = 0, i = e.length, o = sn(n), s = sn(e);
  o.forEach(function(l) {
    for (var u = !1, d = r; d < i; d += 1) {
      var h = s[d];
      if (h.key === l.key) {
        r < d && (t = t.concat(s.slice(r, d).map(function(p) {
          return k(k({}, p), {}, {
            status: nn
          });
        })), r = d), t.push(k(k({}, h), {}, {
          status: rn
        })), r += 1, u = !0;
        break;
      }
    }
    u || t.push(k(k({}, l), {}, {
      status: on
    }));
  }), r < i && (t = t.concat(s.slice(r).map(function(l) {
    return k(k({}, l), {}, {
      status: nn
    });
  })));
  var a = {};
  t.forEach(function(l) {
    var u = l.key;
    a[u] = (a[u] || 0) + 1;
  });
  var c = Object.keys(a).filter(function(l) {
    return a[l] > 1;
  });
  return c.forEach(function(l) {
    t = t.filter(function(u) {
      var d = u.key, h = u.status;
      return d !== l || h !== on;
    }), t.forEach(function(u) {
      u.key === l && (u.status = rn);
    });
  }), t;
}
var ia = ["component", "children", "onVisibleChanged", "onAllRemoved"], oa = ["status"], sa = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function aa(n) {
  var e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : Br, t = /* @__PURE__ */ function(r) {
    vt(o, r);
    var i = bt(o);
    function o() {
      var s;
      De(this, o);
      for (var a = arguments.length, c = new Array(a), l = 0; l < a; l++)
        c[l] = arguments[l];
      return s = i.call.apply(i, [this].concat(c)), D(Te(s), "state", {
        keyEntities: []
      }), D(Te(s), "removeKey", function(u) {
        s.setState(function(d) {
          var h = d.keyEntities.map(function(p) {
            return p.key !== u ? p : k(k({}, p), {}, {
              status: Ht
            });
          });
          return {
            keyEntities: h
          };
        }, function() {
          var d = s.state.keyEntities, h = d.filter(function(p) {
            var v = p.status;
            return v !== Ht;
          }).length;
          h === 0 && s.props.onAllRemoved && s.props.onAllRemoved();
        });
      }), s;
    }
    return Fe(o, [{
      key: "render",
      value: function() {
        var a = this, c = this.state.keyEntities, l = this.props, u = l.component, d = l.children, h = l.onVisibleChanged;
        l.onAllRemoved;
        var p = zn(l, ia), v = u || _.Fragment, g = {};
        return sa.forEach(function(m) {
          g[m] = p[m], delete p[m];
        }), delete p.keys, /* @__PURE__ */ _.createElement(v, p, c.map(function(m, b) {
          var w = m.status, C = zn(m, oa), E = w === nn || w === rn;
          return /* @__PURE__ */ _.createElement(e, ve({}, g, {
            key: C.key,
            visible: E,
            eventProps: C,
            onVisibleChanged: function(x) {
              h == null || h(x, {
                key: C.key
              }), x || a.removeKey(C.key);
            }
          }), function(S, x) {
            return d(k(k({}, S), {}, {
              index: b
            }), x);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, c) {
        var l = a.keys, u = c.keyEntities, d = sn(l), h = ra(u, d);
        return {
          keyEntities: h.filter(function(p) {
            var v = u.find(function(g) {
              var m = g.key;
              return p.key === m;
            });
            return !(v && v.status === Ht && p.status === on);
          })
        };
      }
    }]), o;
  }(_.Component);
  return D(t, "defaultProps", {
    component: "div"
  }), t;
}
const la = aa($r);
function ca(n, e) {
  const {
    children: t,
    upload: r,
    rootClassName: i
  } = n, o = f.useRef(null);
  return f.useImperativeHandle(e, () => o.current), /* @__PURE__ */ f.createElement(dr, ve({}, r, {
    showUploadList: !1,
    rootClassName: i,
    ref: o
  }), t);
}
const Hr = /* @__PURE__ */ f.forwardRef(ca), ua = (n) => {
  const {
    componentCls: e,
    antCls: t,
    calc: r
  } = n, i = `${e}-list-card`, o = r(n.fontSize).mul(n.lineHeight).mul(2).add(n.paddingSM).add(n.paddingSM).equal();
  return {
    [i]: {
      borderRadius: n.borderRadius,
      position: "relative",
      background: n.colorFillContent,
      borderWidth: n.lineWidth,
      borderStyle: "solid",
      borderColor: "transparent",
      flex: "none",
      // =============================== Desc ================================
      [`${i}-name,${i}-desc`]: {
        display: "flex",
        flexWrap: "nowrap",
        maxWidth: "100%"
      },
      [`${i}-ellipsis-prefix`]: {
        flex: "0 1 auto",
        minWidth: 0,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap"
      },
      [`${i}-ellipsis-suffix`]: {
        flex: "none"
      },
      // ============================= Overview ==============================
      "&-type-overview": {
        padding: r(n.paddingSM).sub(n.lineWidth).equal(),
        paddingInlineStart: r(n.padding).add(n.lineWidth).equal(),
        display: "flex",
        flexWrap: "nowrap",
        gap: n.paddingXS,
        alignItems: "flex-start",
        width: 236,
        // Icon
        [`${i}-icon`]: {
          fontSize: r(n.fontSizeLG).mul(2).equal(),
          lineHeight: 1,
          paddingTop: r(n.paddingXXS).mul(1.5).equal(),
          flex: "none"
        },
        // Content
        [`${i}-content`]: {
          flex: "auto",
          minWidth: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch"
        },
        [`${i}-desc`]: {
          color: n.colorTextTertiary
        }
      },
      // ============================== Preview ==============================
      "&-type-preview": {
        width: o,
        height: o,
        lineHeight: 1,
        display: "flex",
        alignItems: "center",
        [`&:not(${i}-status-error)`]: {
          border: 0
        },
        // Img
        [`${t}-image`]: {
          width: "100%",
          height: "100%",
          borderRadius: "inherit",
          position: "relative",
          overflow: "hidden",
          img: {
            height: "100%",
            objectFit: "cover",
            borderRadius: "inherit"
          }
        },
        // Mask
        [`${i}-img-mask`]: {
          position: "absolute",
          inset: 0,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          borderRadius: "inherit",
          background: `rgba(0, 0, 0, ${n.opacityLoading})`
        },
        // Error
        [`&${i}-status-error`]: {
          borderRadius: "inherit",
          [`img, ${i}-img-mask`]: {
            borderRadius: r(n.borderRadius).sub(n.lineWidth).equal()
          },
          [`${i}-desc`]: {
            paddingInline: n.paddingXXS
          }
        },
        // Progress
        [`${i}-progress`]: {}
      },
      // ============================ Remove Icon ============================
      [`${i}-remove`]: {
        position: "absolute",
        top: 0,
        insetInlineEnd: 0,
        border: 0,
        padding: n.paddingXXS,
        background: "transparent",
        lineHeight: 1,
        transform: "translate(50%, -50%)",
        fontSize: n.fontSize,
        cursor: "pointer",
        opacity: n.opacityLoading,
        display: "none",
        "&:dir(rtl)": {
          transform: "translate(-50%, -50%)"
        },
        "&:hover": {
          opacity: 1
        },
        "&:active": {
          opacity: n.opacityLoading
        }
      },
      [`&:hover ${i}-remove`]: {
        display: "block"
      },
      // ============================== Status ===============================
      "&-status-error": {
        borderColor: n.colorError,
        [`${i}-desc`]: {
          color: n.colorError
        }
      },
      // ============================== Motion ===============================
      "&-motion": {
        transition: ["opacity", "width", "margin", "padding"].map((s) => `${s} ${n.motionDurationSlow}`).join(","),
        "&-appear-start": {
          width: 0,
          transition: "none"
        },
        "&-leave-active": {
          opacity: 0,
          width: 0,
          paddingInline: 0,
          borderInlineWidth: 0,
          marginInlineEnd: r(n.paddingSM).mul(-1).equal()
        }
      }
    }
  };
}, an = {
  "&, *": {
    boxSizing: "border-box"
  }
}, da = (n) => {
  const {
    componentCls: e,
    calc: t,
    antCls: r
  } = n, i = `${e}-drop-area`, o = `${e}-placeholder`;
  return {
    // ============================== Full Screen ==============================
    [i]: {
      position: "absolute",
      inset: 0,
      zIndex: n.zIndexPopupBase,
      ...an,
      "&-on-body": {
        position: "fixed",
        inset: 0
      },
      "&-hide-placement": {
        [`${o}-inner`]: {
          display: "none"
        }
      },
      [o]: {
        padding: 0
      }
    },
    "&": {
      // ============================= Placeholder =============================
      [o]: {
        height: "100%",
        borderRadius: n.borderRadius,
        borderWidth: n.lineWidthBold,
        borderStyle: "dashed",
        borderColor: "transparent",
        padding: n.padding,
        position: "relative",
        backdropFilter: "blur(10px)",
        background: n.colorBgPlaceholderHover,
        ...an,
        [`${r}-upload-wrapper ${r}-upload${r}-upload-btn`]: {
          padding: 0
        },
        [`&${o}-drag-in`]: {
          borderColor: n.colorPrimaryHover
        },
        [`&${o}-disabled`]: {
          opacity: 0.25,
          pointerEvents: "none"
        },
        [`${o}-inner`]: {
          gap: t(n.paddingXXS).div(2).equal()
        },
        [`${o}-icon`]: {
          fontSize: n.fontSizeHeading2,
          lineHeight: 1
        },
        [`${o}-title${o}-title`]: {
          margin: 0,
          fontSize: n.fontSize,
          lineHeight: n.lineHeight
        },
        [`${o}-description`]: {}
      }
    }
  };
}, fa = (n) => {
  const {
    componentCls: e,
    calc: t
  } = n, r = `${e}-list`, i = t(n.fontSize).mul(n.lineHeight).mul(2).add(n.paddingSM).add(n.paddingSM).equal();
  return {
    [e]: {
      position: "relative",
      width: "100%",
      ...an,
      // =============================== File List ===============================
      [r]: {
        display: "flex",
        flexWrap: "wrap",
        gap: n.paddingSM,
        fontSize: n.fontSize,
        lineHeight: n.lineHeight,
        color: n.colorText,
        paddingBlock: n.paddingSM,
        paddingInline: n.padding,
        width: "100%",
        background: n.colorBgContainer,
        // Hide scrollbar
        scrollbarWidth: "none",
        "-ms-overflow-style": "none",
        "&::-webkit-scrollbar": {
          display: "none"
        },
        // Scroll
        "&-overflow-scrollX, &-overflow-scrollY": {
          "&:before, &:after": {
            content: '""',
            position: "absolute",
            opacity: 0,
            transition: `opacity ${n.motionDurationSlow}`,
            zIndex: 1
          }
        },
        "&-overflow-ping-start:before": {
          opacity: 1
        },
        "&-overflow-ping-end:after": {
          opacity: 1
        },
        "&-overflow-scrollX": {
          overflowX: "auto",
          overflowY: "hidden",
          flexWrap: "nowrap",
          "&:before, &:after": {
            insetBlock: 0,
            width: 8
          },
          "&:before": {
            insetInlineStart: 0,
            background: "linear-gradient(to right, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          },
          "&:after": {
            insetInlineEnd: 0,
            background: "linear-gradient(to left, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          },
          "&:dir(rtl)": {
            "&:before": {
              background: "linear-gradient(to left, rgba(0,0,0,0.06), rgba(0,0,0,0));"
            },
            "&:after": {
              background: "linear-gradient(to right, rgba(0,0,0,0.06), rgba(0,0,0,0));"
            }
          }
        },
        "&-overflow-scrollY": {
          overflowX: "hidden",
          overflowY: "auto",
          maxHeight: t(i).mul(3).equal(),
          "&:before, &:after": {
            insetInline: 0,
            height: 8
          },
          "&:before": {
            insetBlockStart: 0,
            background: "linear-gradient(to bottom, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          },
          "&:after": {
            insetBlockEnd: 0,
            background: "linear-gradient(to top, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          }
        },
        // ======================================================================
        // ==                              Upload                              ==
        // ======================================================================
        "&-upload-btn": {
          width: i,
          height: i,
          fontSize: n.fontSizeHeading2,
          color: "#999"
        },
        // ======================================================================
        // ==                             PrevNext                             ==
        // ======================================================================
        "&-prev-btn, &-next-btn": {
          position: "absolute",
          top: "50%",
          transform: "translateY(-50%)",
          boxShadow: n.boxShadowTertiary,
          opacity: 0,
          pointerEvents: "none"
        },
        "&-prev-btn": {
          left: {
            _skip_check_: !0,
            value: n.padding
          }
        },
        "&-next-btn": {
          right: {
            _skip_check_: !0,
            value: n.padding
          }
        },
        "&:dir(ltr)": {
          [`&${r}-overflow-ping-start ${r}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${r}-overflow-ping-end ${r}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        },
        "&:dir(rtl)": {
          [`&${r}-overflow-ping-end ${r}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${r}-overflow-ping-start ${r}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        }
      }
    }
  };
}, ha = (n) => {
  const {
    colorBgContainer: e
  } = n;
  return {
    colorBgPlaceholderHover: new xe(e).setA(0.85).toRgbString()
  };
}, zr = Tr("Attachments", (n) => {
  const e = Lt(n, {});
  return [da(e), fa(e), ua(e)];
}, ha), pa = (n) => n.indexOf("image/") === 0, et = 200;
function ma(n) {
  return new Promise((e) => {
    if (!n || !n.type || !pa(n.type)) {
      e("");
      return;
    }
    const t = new Image();
    if (t.onload = () => {
      const {
        width: r,
        height: i
      } = t, o = r / i, s = o > 1 ? et : et * o, a = o > 1 ? et / o : et, c = document.createElement("canvas");
      c.width = s, c.height = a, c.style.cssText = `position: fixed; left: 0; top: 0; width: ${s}px; height: ${a}px; z-index: 9999; display: none;`, document.body.appendChild(c), c.getContext("2d").drawImage(t, 0, 0, s, a);
      const u = c.toDataURL();
      document.body.removeChild(c), window.URL.revokeObjectURL(t.src), e(u);
    }, t.crossOrigin = "anonymous", n.type.startsWith("image/svg+xml")) {
      const r = new FileReader();
      r.onload = () => {
        r.result && typeof r.result == "string" && (t.src = r.result);
      }, r.readAsDataURL(n);
    } else if (n.type.startsWith("image/gif")) {
      const r = new FileReader();
      r.onload = () => {
        r.result && e(r.result);
      }, r.readAsDataURL(n);
    } else
      t.src = window.URL.createObjectURL(n);
  });
}
function ga() {
  return /* @__PURE__ */ f.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    //xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ f.createElement("title", null, "audio"), /* @__PURE__ */ f.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ f.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M10.7315824,7.11216117 C10.7428131,7.15148751 10.7485063,7.19218979 10.7485063,7.23309113 L10.7485063,8.07742614 C10.7484199,8.27364959 10.6183424,8.44607275 10.4296853,8.50003683 L8.32984514,9.09986306 L8.32984514,11.7071803 C8.32986605,12.5367078 7.67249692,13.217028 6.84345686,13.2454634 L6.79068592,13.2463395 C6.12766108,13.2463395 5.53916361,12.8217001 5.33010655,12.1924966 C5.1210495,11.563293 5.33842118,10.8709227 5.86959669,10.4741173 C6.40077221,10.0773119 7.12636292,10.0652587 7.67042486,10.4442027 L7.67020842,7.74937024 L7.68449368,7.74937024 C7.72405122,7.59919041 7.83988806,7.48101083 7.98924584,7.4384546 L10.1880418,6.81004755 C10.42156,6.74340323 10.6648954,6.87865515 10.7315824,7.11216117 Z M9.60714286,1.31785714 L12.9678571,4.67857143 L9.60714286,4.67857143 L9.60714286,1.31785714 Z",
    fill: "currentColor"
  })));
}
function va(n) {
  const {
    percent: e
  } = n, {
    token: t
  } = dt.useToken();
  return /* @__PURE__ */ f.createElement(Ni, {
    type: "circle",
    percent: e,
    size: t.fontSizeHeading2 * 2,
    strokeColor: "#FFF",
    trailColor: "rgba(255, 255, 255, 0.3)",
    format: (r) => /* @__PURE__ */ f.createElement("span", {
      style: {
        color: "#FFF"
      }
    }, (r || 0).toFixed(0), "%")
  });
}
function ba() {
  return /* @__PURE__ */ f.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    // xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ f.createElement("title", null, "video"), /* @__PURE__ */ f.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ f.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M12.9678571,4.67857143 L9.60714286,1.31785714 L9.60714286,4.67857143 L12.9678571,4.67857143 Z M10.5379461,10.3101106 L6.68957555,13.0059749 C6.59910784,13.0693494 6.47439406,13.0473861 6.41101953,12.9569184 C6.3874624,12.9232903 6.37482581,12.8832269 6.37482581,12.8421686 L6.37482581,7.45043999 C6.37482581,7.33998304 6.46436886,7.25043999 6.57482581,7.25043999 C6.61588409,7.25043999 6.65594753,7.26307658 6.68957555,7.28663371 L10.5379461,9.98249803 C10.6284138,10.0458726 10.6503772,10.1705863 10.5870027,10.2610541 C10.5736331,10.2801392 10.5570312,10.2967411 10.5379461,10.3101106 Z",
    fill: "currentColor"
  })));
}
const zt = " ", at = "#8c8c8c", Ur = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"], Yn = [{
  key: "default",
  icon: /* @__PURE__ */ f.createElement(ur, null),
  color: at,
  ext: []
}, {
  key: "excel",
  icon: /* @__PURE__ */ f.createElement(wi, null),
  color: "#22b35e",
  ext: ["xlsx", "xls"]
}, {
  key: "image",
  icon: /* @__PURE__ */ f.createElement(Si, null),
  color: at,
  ext: Ur
}, {
  key: "markdown",
  icon: /* @__PURE__ */ f.createElement(xi, null),
  color: at,
  ext: ["md", "mdx"]
}, {
  key: "pdf",
  icon: /* @__PURE__ */ f.createElement(Ci, null),
  color: "#ff4d4f",
  ext: ["pdf"]
}, {
  key: "ppt",
  icon: /* @__PURE__ */ f.createElement(Ei, null),
  color: "#ff6e31",
  ext: ["ppt", "pptx"]
}, {
  key: "word",
  icon: /* @__PURE__ */ f.createElement(_i, null),
  color: "#1677ff",
  ext: ["doc", "docx"]
}, {
  key: "zip",
  icon: /* @__PURE__ */ f.createElement(Ri, null),
  color: "#fab714",
  ext: ["zip", "rar", "7z", "tar", "gz"]
}, {
  key: "video",
  icon: /* @__PURE__ */ f.createElement(ba, null),
  color: "#ff4d4f",
  ext: ["mp4", "avi", "mov", "wmv", "flv", "mkv"]
}, {
  key: "audio",
  icon: /* @__PURE__ */ f.createElement(ga, null),
  color: "#8c8c8c",
  ext: ["mp3", "wav", "flac", "ape", "aac", "ogg"]
}];
function Zn(n, e) {
  return e.some((t) => n.toLowerCase() === `.${t}`);
}
function ya(n) {
  let e = n;
  const t = ["B", "KB", "MB", "GB", "TB", "PB", "EB"];
  let r = 0;
  for (; e >= 1024 && r < t.length - 1; )
    e /= 1024, r++;
  return `${e.toFixed(0)} ${t[r]}`;
}
function wa(n, e) {
  const {
    prefixCls: t,
    item: r,
    onRemove: i,
    className: o,
    style: s,
    imageProps: a,
    type: c,
    icon: l
  } = n, u = f.useContext(Xe), {
    disabled: d
  } = u || {}, {
    name: h,
    size: p,
    percent: v,
    status: g = "done",
    description: m
  } = r, {
    getPrefixCls: b
  } = Ue(), w = b("attachment", t), C = `${w}-list-card`, [E, S, x] = zr(w), [T, R] = f.useMemo(() => {
    const I = h || "", y = I.match(/^(.*)\.[^.]+$/);
    return y ? [y[1], I.slice(y[1].length)] : [I, ""];
  }, [h]), O = f.useMemo(() => Zn(R, Ur), [R]), P = f.useMemo(() => m || (g === "uploading" ? `${v || 0}%` : g === "error" ? r.response || zt : p ? ya(p) : zt), [g, v]), [M, $] = f.useMemo(() => {
    if (l)
      if (typeof l == "string") {
        const I = Yn.find((y) => y.key === l);
        if (I)
          return [I.icon, I.color];
      } else
        return [l, void 0];
    for (const {
      ext: I,
      icon: y,
      color: le
    } of Yn)
      if (Zn(R, I))
        return [y, le];
    return [/* @__PURE__ */ f.createElement(ur, {
      key: "defaultIcon"
    }), at];
  }, [R, l]), [N, W] = f.useState();
  f.useEffect(() => {
    if (r.originFileObj) {
      let I = !0;
      return ma(r.originFileObj).then((y) => {
        I && W(y);
      }), () => {
        I = !1;
      };
    }
    W(void 0);
  }, [r.originFileObj]);
  let A = null;
  const U = r.thumbUrl || r.url || N, F = c === "image" || c !== "file" && O && (r.originFileObj || U);
  return F ? A = /* @__PURE__ */ f.createElement(f.Fragment, null, U && /* @__PURE__ */ f.createElement(ji, ve({
    alt: "preview",
    src: U
  }, a)), g !== "done" && /* @__PURE__ */ f.createElement("div", {
    className: `${C}-img-mask`
  }, g === "uploading" && v !== void 0 && /* @__PURE__ */ f.createElement(va, {
    percent: v,
    prefixCls: C
  }), g === "error" && /* @__PURE__ */ f.createElement("div", {
    className: `${C}-desc`
  }, /* @__PURE__ */ f.createElement("div", {
    className: `${C}-ellipsis-prefix`
  }, P)))) : A = /* @__PURE__ */ f.createElement(f.Fragment, null, /* @__PURE__ */ f.createElement("div", {
    className: `${C}-icon`,
    style: $ ? {
      color: $
    } : void 0
  }, M), /* @__PURE__ */ f.createElement("div", {
    className: `${C}-content`
  }, /* @__PURE__ */ f.createElement("div", {
    className: `${C}-name`
  }, /* @__PURE__ */ f.createElement("div", {
    className: `${C}-ellipsis-prefix`
  }, T ?? zt), /* @__PURE__ */ f.createElement("div", {
    className: `${C}-ellipsis-suffix`
  }, R)), /* @__PURE__ */ f.createElement("div", {
    className: `${C}-desc`
  }, /* @__PURE__ */ f.createElement("div", {
    className: `${C}-ellipsis-prefix`
  }, P)))), E(/* @__PURE__ */ f.createElement("div", {
    className: K(C, {
      [`${C}-status-${g}`]: g,
      [`${C}-type-preview`]: F,
      [`${C}-type-overview`]: !F
    }, o, S, x),
    style: s,
    ref: e
  }, A, !d && i && /* @__PURE__ */ f.createElement("button", {
    type: "button",
    className: `${C}-remove`,
    onClick: () => {
      i(r);
    }
  }, /* @__PURE__ */ f.createElement(yi, null))));
}
const Vr = /* @__PURE__ */ f.forwardRef(wa), Qn = 1;
function Sa(n) {
  const {
    prefixCls: e,
    items: t,
    onRemove: r,
    overflow: i,
    upload: o,
    listClassName: s,
    listStyle: a,
    itemClassName: c,
    uploadClassName: l,
    uploadStyle: u,
    itemStyle: d,
    imageProps: h
  } = n, p = `${e}-list`, v = f.useRef(null), [g, m] = f.useState(!1), {
    disabled: b
  } = f.useContext(Xe);
  f.useEffect(() => (m(!0), () => {
    m(!1);
  }), []);
  const [w, C] = f.useState(!1), [E, S] = f.useState(!1), x = () => {
    const P = v.current;
    P && (i === "scrollX" ? (C(Math.abs(P.scrollLeft) >= Qn), S(P.scrollWidth - P.clientWidth - Math.abs(P.scrollLeft) >= Qn)) : i === "scrollY" && (C(P.scrollTop !== 0), S(P.scrollHeight - P.clientHeight !== P.scrollTop)));
  };
  f.useEffect(() => {
    x();
  }, [i, t.length]);
  const T = (P) => {
    const M = v.current;
    M && M.scrollTo({
      left: M.scrollLeft + P * M.clientWidth,
      behavior: "smooth"
    });
  }, R = () => {
    T(-1);
  }, O = () => {
    T(1);
  };
  return /* @__PURE__ */ f.createElement("div", {
    className: K(p, {
      [`${p}-overflow-${n.overflow}`]: i,
      [`${p}-overflow-ping-start`]: w,
      [`${p}-overflow-ping-end`]: E
    }, s),
    ref: v,
    onScroll: x,
    style: a
  }, /* @__PURE__ */ f.createElement(la, {
    keys: t.map((P) => ({
      key: P.uid,
      item: P
    })),
    motionName: `${p}-card-motion`,
    component: !1,
    motionAppear: g,
    motionLeave: !0,
    motionEnter: !0
  }, ({
    key: P,
    item: M,
    className: $,
    style: N
  }) => /* @__PURE__ */ f.createElement(Vr, {
    key: P,
    prefixCls: e,
    item: M,
    onRemove: r,
    className: K($, c),
    imageProps: h,
    style: {
      ...N,
      ...d
    }
  })), !b && /* @__PURE__ */ f.createElement(Hr, {
    upload: o
  }, /* @__PURE__ */ f.createElement(ke, {
    className: K(l, `${p}-upload-btn`),
    style: u,
    type: "dashed"
  }, /* @__PURE__ */ f.createElement(Pi, {
    className: `${p}-upload-btn-icon`
  }))), i === "scrollX" && /* @__PURE__ */ f.createElement(f.Fragment, null, /* @__PURE__ */ f.createElement(ke, {
    size: "small",
    shape: "circle",
    className: `${p}-prev-btn`,
    icon: /* @__PURE__ */ f.createElement(Ti, null),
    onClick: R
  }), /* @__PURE__ */ f.createElement(ke, {
    size: "small",
    shape: "circle",
    className: `${p}-next-btn`,
    icon: /* @__PURE__ */ f.createElement(Mi, null),
    onClick: O
  })));
}
function xa(n, e) {
  const {
    prefixCls: t,
    placeholder: r = {},
    upload: i,
    className: o,
    style: s
  } = n, a = `${t}-placeholder`, c = r || {}, {
    disabled: l
  } = f.useContext(Xe), [u, d] = f.useState(!1), h = () => {
    d(!0);
  }, p = (m) => {
    m.currentTarget.contains(m.relatedTarget) || d(!1);
  }, v = () => {
    d(!1);
  }, g = /* @__PURE__ */ f.isValidElement(r) ? r : /* @__PURE__ */ f.createElement(ft, {
    align: "center",
    justify: "center",
    vertical: !0,
    className: `${a}-inner`
  }, /* @__PURE__ */ f.createElement(It.Text, {
    className: `${a}-icon`
  }, c.icon), /* @__PURE__ */ f.createElement(It.Title, {
    className: `${a}-title`,
    level: 5
  }, c.title), /* @__PURE__ */ f.createElement(It.Text, {
    className: `${a}-description`,
    type: "secondary"
  }, c.description));
  return /* @__PURE__ */ f.createElement("div", {
    className: K(a, {
      [`${a}-drag-in`]: u,
      [`${a}-disabled`]: l
    }, o),
    onDragEnter: h,
    onDragLeave: p,
    onDrop: v,
    "aria-hidden": l,
    style: s
  }, /* @__PURE__ */ f.createElement(dr.Dragger, ve({
    showUploadList: !1
  }, i, {
    ref: e,
    style: {
      padding: 0,
      border: 0,
      background: "transparent"
    }
  }), g));
}
const Ca = /* @__PURE__ */ f.forwardRef(xa);
function Ea(n, e) {
  const {
    prefixCls: t,
    rootClassName: r,
    rootStyle: i,
    className: o,
    style: s,
    items: a,
    children: c,
    getDropContainer: l,
    placeholder: u,
    onChange: d,
    onRemove: h,
    overflow: p,
    imageProps: v,
    disabled: g,
    maxCount: m,
    classNames: b = {},
    styles: w = {},
    ...C
  } = n, {
    getPrefixCls: E,
    direction: S
  } = Ue(), x = E("attachment", t), T = br("attachments"), {
    classNames: R,
    styles: O
  } = T, P = f.useRef(null), M = f.useRef(null);
  f.useImperativeHandle(e, () => ({
    nativeElement: P.current,
    upload: (V) => {
      var Q, te;
      const z = (te = (Q = M.current) == null ? void 0 : Q.nativeElement) == null ? void 0 : te.querySelector('input[type="file"]');
      if (z) {
        const ce = new DataTransfer();
        ce.items.add(V), z.files = ce.files, z.dispatchEvent(new Event("change", {
          bubbles: !0
        }));
      }
    }
  }));
  const [$, N, W] = zr(x), A = K(N, W), [U, F] = cn([], {
    value: a
  }), I = Re((V) => {
    F(V.fileList), d == null || d(V);
  }), y = {
    ...C,
    fileList: U,
    maxCount: m,
    onChange: I
  }, le = (V) => Promise.resolve(typeof h == "function" ? h(V) : h).then((z) => {
    if (z === !1)
      return;
    const Q = U.filter((te) => te.uid !== V.uid);
    I({
      file: {
        ...V,
        status: "removed"
      },
      fileList: Q
    });
  });
  let ee;
  const J = (V, z, Q) => {
    const te = typeof u == "function" ? u(V) : u;
    return /* @__PURE__ */ f.createElement(Ca, {
      placeholder: te,
      upload: y,
      prefixCls: x,
      className: K(R.placeholder, b.placeholder),
      style: {
        ...O.placeholder,
        ...w.placeholder,
        ...z == null ? void 0 : z.style
      },
      ref: Q
    });
  };
  if (c)
    ee = /* @__PURE__ */ f.createElement(f.Fragment, null, /* @__PURE__ */ f.createElement(Hr, {
      upload: y,
      rootClassName: r,
      ref: M
    }, c), /* @__PURE__ */ f.createElement(Bn, {
      getDropContainer: l,
      prefixCls: x,
      className: K(A, r)
    }, J("drop")));
  else {
    const V = U.length > 0;
    ee = /* @__PURE__ */ f.createElement("div", {
      className: K(x, A, {
        [`${x}-rtl`]: S === "rtl"
      }, o, r),
      style: {
        ...i,
        ...s
      },
      dir: S || "ltr",
      ref: P
    }, /* @__PURE__ */ f.createElement(Sa, {
      prefixCls: x,
      items: U,
      onRemove: le,
      overflow: p,
      upload: y,
      listClassName: K(R.list, b.list),
      listStyle: {
        ...O.list,
        ...w.list,
        ...!V && {
          display: "none"
        }
      },
      uploadClassName: K(R.upload, b.upload),
      uploadStyle: {
        ...O.upload,
        ...w.upload
      },
      itemClassName: K(R.item, b.item),
      itemStyle: {
        ...O.item,
        ...w.item
      },
      imageProps: v
    }), J("inline", V ? {
      style: {
        display: "none"
      }
    } : {}, M), /* @__PURE__ */ f.createElement(Bn, {
      getDropContainer: l || (() => P.current),
      prefixCls: x,
      className: A
    }, J("drop")));
  }
  return $(/* @__PURE__ */ f.createElement(Xe.Provider, {
    value: {
      disabled: g
    }
  }, ee));
}
const Xr = /* @__PURE__ */ f.forwardRef(Ea);
Xr.FileCard = Vr;
function _a(n, e) {
  return ai(n, () => {
    const t = e(), {
      nativeElement: r
    } = t;
    return new Proxy(r, {
      get(i, o) {
        return t[o] ? t[o] : Reflect.get(i, o);
      }
    });
  });
}
const Gr = /* @__PURE__ */ _.createContext({}), Jn = () => ({
  height: 0
}), er = (n) => ({
  height: n.scrollHeight
});
function Ra(n) {
  const {
    title: e,
    onOpenChange: t,
    open: r,
    children: i,
    className: o,
    style: s,
    classNames: a = {},
    styles: c = {},
    closable: l,
    forceRender: u
  } = n, {
    prefixCls: d
  } = _.useContext(Gr), h = `${d}-header`;
  return /* @__PURE__ */ _.createElement(Br, {
    motionEnter: !0,
    motionLeave: !0,
    motionName: `${h}-motion`,
    leavedClassName: `${h}-motion-hidden`,
    onEnterStart: Jn,
    onEnterActive: er,
    onLeaveStart: er,
    onLeaveActive: Jn,
    visible: r,
    forceRender: u
  }, ({
    className: p,
    style: v
  }) => /* @__PURE__ */ _.createElement("div", {
    className: K(h, p, o),
    style: {
      ...v,
      ...s
    }
  }, (l !== !1 || e) && /* @__PURE__ */ _.createElement("div", {
    className: (
      // We follow antd naming standard here.
      // So the header part is use `-header` suffix.
      // Though its little bit weird for double `-header`.
      K(`${h}-header`, a.header)
    ),
    style: {
      ...c.header
    }
  }, /* @__PURE__ */ _.createElement("div", {
    className: `${h}-title`
  }, e), l !== !1 && /* @__PURE__ */ _.createElement("div", {
    className: `${h}-close`
  }, /* @__PURE__ */ _.createElement(ke, {
    type: "text",
    icon: /* @__PURE__ */ _.createElement(Li, null),
    size: "small",
    onClick: () => {
      t == null || t(!r);
    }
  }))), i && /* @__PURE__ */ _.createElement("div", {
    className: K(`${h}-content`, a.content),
    style: {
      ...c.content
    }
  }, i)));
}
const Ot = /* @__PURE__ */ _.createContext(null);
function Pa(n, e) {
  const {
    className: t,
    action: r,
    onClick: i,
    ...o
  } = n, s = _.useContext(Ot), {
    prefixCls: a,
    disabled: c
  } = s, l = o.disabled ?? c ?? s[`${r}Disabled`];
  return /* @__PURE__ */ _.createElement(ke, ve({
    type: "text"
  }, o, {
    ref: e,
    onClick: (u) => {
      var d;
      l || ((d = s[r]) == null || d.call(s), i == null || i(u));
    },
    className: K(a, t, {
      [`${a}-disabled`]: l
    })
  }));
}
const At = /* @__PURE__ */ _.forwardRef(Pa);
function Ta(n, e) {
  return /* @__PURE__ */ _.createElement(At, ve({
    icon: /* @__PURE__ */ _.createElement(Oi, null)
  }, n, {
    action: "onClear",
    ref: e
  }));
}
const Ma = /* @__PURE__ */ _.forwardRef(Ta), La = /* @__PURE__ */ li((n) => {
  const {
    className: e
  } = n;
  return /* @__PURE__ */ f.createElement("svg", {
    color: "currentColor",
    viewBox: "0 0 1000 1000",
    xmlns: "http://www.w3.org/2000/svg",
    className: e
  }, /* @__PURE__ */ f.createElement("title", null, "Stop Loading"), /* @__PURE__ */ f.createElement("rect", {
    fill: "currentColor",
    height: "250",
    rx: "24",
    ry: "24",
    width: "250",
    x: "375",
    y: "375"
  }), /* @__PURE__ */ f.createElement("circle", {
    cx: "500",
    cy: "500",
    fill: "none",
    r: "450",
    stroke: "currentColor",
    strokeWidth: "100",
    opacity: "0.45"
  }), /* @__PURE__ */ f.createElement("circle", {
    cx: "500",
    cy: "500",
    fill: "none",
    r: "450",
    stroke: "currentColor",
    strokeWidth: "100",
    strokeDasharray: "600 9999999"
  }, /* @__PURE__ */ f.createElement("animateTransform", {
    attributeName: "transform",
    dur: "1s",
    from: "0 500 500",
    repeatCount: "indefinite",
    to: "360 500 500",
    type: "rotate"
  })));
});
function Oa(n, e) {
  const {
    prefixCls: t
  } = _.useContext(Ot), {
    className: r
  } = n;
  return /* @__PURE__ */ _.createElement(At, ve({
    icon: /* @__PURE__ */ _.createElement(La, {
      className: `${t}-loading-icon`
    }),
    color: "primary",
    variant: "text",
    shape: "circle"
  }, n, {
    className: K(r, `${t}-loading-button`),
    action: "onCancel",
    ref: e
  }));
}
const qr = /* @__PURE__ */ _.forwardRef(Oa);
function Aa(n, e) {
  return /* @__PURE__ */ _.createElement(At, ve({
    icon: /* @__PURE__ */ _.createElement(Ai, null),
    type: "primary",
    shape: "circle"
  }, n, {
    action: "onSend",
    ref: e
  }));
}
const Kr = /* @__PURE__ */ _.forwardRef(Aa), Be = 1e3, He = 4, lt = 140, tr = lt / 2, tt = 250, nr = 500, nt = 0.8;
function Ia({
  className: n
}) {
  return /* @__PURE__ */ f.createElement("svg", {
    color: "currentColor",
    viewBox: `0 0 ${Be} ${Be}`,
    xmlns: "http://www.w3.org/2000/svg",
    className: n
  }, /* @__PURE__ */ f.createElement("title", null, "Speech Recording"), Array.from({
    length: He
  }).map((e, t) => {
    const r = (Be - lt * He) / (He - 1), i = t * (r + lt), o = Be / 2 - tt / 2, s = Be / 2 - nr / 2;
    return /* @__PURE__ */ f.createElement("rect", {
      fill: "currentColor",
      rx: tr,
      ry: tr,
      height: tt,
      width: lt,
      x: i,
      y: o,
      key: t
    }, /* @__PURE__ */ f.createElement("animate", {
      attributeName: "height",
      values: `${tt}; ${nr}; ${tt}`,
      keyTimes: "0; 0.5; 1",
      dur: `${nt}s`,
      begin: `${nt / He * t}s`,
      repeatCount: "indefinite"
    }), /* @__PURE__ */ f.createElement("animate", {
      attributeName: "y",
      values: `${o}; ${s}; ${o}`,
      keyTimes: "0; 0.5; 1",
      dur: `${nt}s`,
      begin: `${nt / He * t}s`,
      repeatCount: "indefinite"
    }));
  }));
}
function $a(n, e) {
  const {
    speechRecording: t,
    onSpeechDisabled: r,
    prefixCls: i
  } = _.useContext(Ot);
  let o = null;
  return t ? o = /* @__PURE__ */ _.createElement(Ia, {
    className: `${i}-recording-icon`
  }) : r ? o = /* @__PURE__ */ _.createElement(Ii, null) : o = /* @__PURE__ */ _.createElement($i, null), /* @__PURE__ */ _.createElement(At, ve({
    icon: o,
    color: "primary",
    variant: "text"
  }, n, {
    action: "onSpeech",
    ref: e
  }));
}
const Yr = /* @__PURE__ */ _.forwardRef($a), ka = (n) => {
  const {
    componentCls: e,
    calc: t
  } = n, r = `${e}-header`;
  return {
    [e]: {
      [r]: {
        borderBottomWidth: n.lineWidth,
        borderBottomStyle: "solid",
        borderBottomColor: n.colorBorder,
        // ======================== Header ========================
        "&-header": {
          background: n.colorFillAlter,
          fontSize: n.fontSize,
          lineHeight: n.lineHeight,
          paddingBlock: t(n.paddingSM).sub(n.lineWidthBold).equal(),
          paddingInlineStart: n.padding,
          paddingInlineEnd: n.paddingXS,
          display: "flex",
          borderRadius: {
            _skip_check_: !0,
            value: t(n.borderRadius).mul(2).equal()
          },
          borderEndStartRadius: 0,
          borderEndEndRadius: 0,
          [`${r}-title`]: {
            flex: "auto"
          }
        },
        // ======================= Content ========================
        "&-content": {
          padding: n.padding
        },
        // ======================== Motion ========================
        "&-motion": {
          transition: ["height", "border"].map((i) => `${i} ${n.motionDurationSlow}`).join(","),
          overflow: "hidden",
          "&-enter-start, &-leave-active": {
            borderBottomColor: "transparent"
          },
          "&-hidden": {
            display: "none"
          }
        }
      }
    }
  };
}, Da = (n) => {
  const {
    componentCls: e,
    padding: t,
    paddingSM: r,
    paddingXS: i,
    paddingXXS: o,
    lineWidth: s,
    lineWidthBold: a,
    calc: c
  } = n;
  return {
    [e]: {
      position: "relative",
      width: "100%",
      boxSizing: "border-box",
      boxShadow: `${n.boxShadowTertiary}`,
      transition: `background ${n.motionDurationSlow}`,
      // Border
      borderRadius: {
        _skip_check_: !0,
        value: c(n.borderRadius).mul(2).equal()
      },
      borderColor: n.colorBorder,
      borderWidth: 0,
      borderStyle: "solid",
      // Border
      "&:after": {
        content: '""',
        position: "absolute",
        inset: 0,
        pointerEvents: "none",
        transition: `border-color ${n.motionDurationSlow}`,
        borderRadius: {
          _skip_check_: !0,
          value: "inherit"
        },
        borderStyle: "inherit",
        borderColor: "inherit",
        borderWidth: s
      },
      // Focus
      "&:focus-within": {
        boxShadow: `${n.boxShadowSecondary}`,
        borderColor: n.colorPrimary,
        "&:after": {
          borderWidth: a
        }
      },
      "&-disabled": {
        background: n.colorBgContainerDisabled
      },
      // ============================== RTL ==============================
      [`&${e}-rtl`]: {
        direction: "rtl"
      },
      // ============================ Content ============================
      [`${e}-content`]: {
        display: "flex",
        gap: i,
        width: "100%",
        paddingBlock: r,
        paddingInlineStart: t,
        paddingInlineEnd: r,
        boxSizing: "border-box",
        alignItems: "flex-end"
      },
      // ============================ Prefix =============================
      [`${e}-prefix`]: {
        flex: "none"
      },
      // ============================= Input =============================
      [`${e}-input`]: {
        padding: 0,
        borderRadius: 0,
        flex: "auto",
        alignSelf: "center",
        minHeight: "auto"
      },
      // ============================ Actions ============================
      [`${e}-actions-list`]: {
        flex: "none",
        display: "flex",
        "&-presets": {
          gap: n.paddingXS
        }
      },
      [`${e}-actions-btn`]: {
        "&-disabled": {
          opacity: 0.45
        },
        "&-loading-button": {
          padding: 0,
          border: 0
        },
        "&-loading-icon": {
          height: n.controlHeight,
          width: n.controlHeight,
          verticalAlign: "top"
        },
        "&-recording-icon": {
          height: "1.2em",
          width: "1.2em",
          verticalAlign: "top"
        }
      },
      // ============================ Footer =============================
      [`${e}-footer`]: {
        paddingInlineStart: t,
        paddingInlineEnd: r,
        paddingBlockEnd: r,
        paddingBlockStart: o,
        boxSizing: "border-box"
      }
    }
  };
}, Fa = () => ({}), Na = Tr("Sender", (n) => {
  const {
    paddingXS: e,
    calc: t
  } = n, r = Lt(n, {
    SenderContentMaxWidth: `calc(100% - ${Yt(t(e).add(32).equal())})`
  });
  return [Da(r), ka(r)];
}, Fa);
let mt;
!mt && typeof window < "u" && (mt = window.SpeechRecognition || window.webkitSpeechRecognition);
function ja(n, e) {
  const t = Re(n), [r, i, o] = f.useMemo(() => typeof e == "object" ? [e.recording, e.onRecordingChange, typeof e.recording == "boolean"] : [void 0, void 0, !1], [e]), [s, a] = f.useState(null);
  f.useEffect(() => {
    if (typeof navigator < "u" && "permissions" in navigator) {
      let g = null;
      return navigator.permissions.query({
        name: "microphone"
      }).then((m) => {
        a(m.state), m.onchange = function() {
          a(this.state);
        }, g = m;
      }), () => {
        g && (g.onchange = null);
      };
    }
  }, []);
  const c = mt && s !== "denied", l = f.useRef(null), [u, d] = cn(!1, {
    value: r
  }), h = f.useRef(!1), p = () => {
    if (c && !l.current) {
      const g = new mt();
      g.onstart = () => {
        d(!0);
      }, g.onend = () => {
        d(!1);
      }, g.onresult = (m) => {
        var b, w, C;
        if (!h.current) {
          const E = (C = (w = (b = m.results) == null ? void 0 : b[0]) == null ? void 0 : w[0]) == null ? void 0 : C.transcript;
          t(E);
        }
        h.current = !1;
      }, l.current = g;
    }
  }, v = Re((g) => {
    g && !u || (h.current = g, o ? i == null || i(!u) : (p(), l.current && (u ? (l.current.stop(), i == null || i(!1)) : (l.current.start(), i == null || i(!0)))));
  });
  return [c, v, u];
}
function Wa(n, e, t) {
  return Ss(n, e) || t;
}
const rr = {
  SendButton: Kr,
  ClearButton: Ma,
  LoadingButton: qr,
  SpeechButton: Yr
}, Ba = /* @__PURE__ */ f.forwardRef((n, e) => {
  const {
    prefixCls: t,
    styles: r = {},
    classNames: i = {},
    className: o,
    rootClassName: s,
    style: a,
    defaultValue: c,
    value: l,
    readOnly: u,
    submitType: d = "enter",
    onSubmit: h,
    loading: p,
    components: v,
    onCancel: g,
    onChange: m,
    actions: b,
    onKeyPress: w,
    onKeyDown: C,
    disabled: E,
    allowSpeech: S,
    prefix: x,
    footer: T,
    header: R,
    onPaste: O,
    onPasteFile: P,
    autoSize: M = {
      maxRows: 8
    },
    ...$
  } = n, {
    direction: N,
    getPrefixCls: W
  } = Ue(), A = W("sender", t), U = f.useRef(null), F = f.useRef(null);
  _a(e, () => {
    var Z, de;
    return {
      nativeElement: U.current,
      focus: (Z = F.current) == null ? void 0 : Z.focus,
      blur: (de = F.current) == null ? void 0 : de.blur
    };
  });
  const I = br("sender"), y = `${A}-input`, [le, ee, J] = Na(A), V = K(A, I.className, o, s, ee, J, {
    [`${A}-rtl`]: N === "rtl",
    [`${A}-disabled`]: E
  }), z = `${A}-actions-btn`, Q = `${A}-actions-list`, [te, ce] = cn(c || "", {
    value: l
  }), Se = (Z, de) => {
    ce(Z), m && m(Z, de);
  }, [B, L, j] = ja((Z) => {
    Se(`${te} ${Z}`);
  }, S), ne = Wa(v, ["input"], Wi.TextArea), re = {
    ...Go($, {
      attr: !0,
      aria: !0,
      data: !0
    }),
    ref: F
  }, pe = () => {
    te && h && !p && h(te);
  }, se = () => {
    Se("");
  }, X = f.useRef(!1), me = () => {
    X.current = !0;
  }, ye = () => {
    X.current = !1;
  }, G = (Z) => {
    const de = Z.key === "Enter" && !X.current;
    switch (d) {
      case "enter":
        de && !Z.shiftKey && (Z.preventDefault(), pe());
        break;
      case "shiftEnter":
        de && Z.shiftKey && (Z.preventDefault(), pe());
        break;
    }
    w == null || w(Z);
  }, ie = (Z) => {
    var Ne;
    const de = (Ne = Z.clipboardData) == null ? void 0 : Ne.files;
    de != null && de.length && P && (P(de[0], de), Z.preventDefault()), O == null || O(Z);
  }, oe = (Z) => {
    var de, Ne;
    Z.target !== ((de = U.current) == null ? void 0 : de.querySelector(`.${y}`)) && Z.preventDefault(), (Ne = F.current) == null || Ne.focus();
  };
  let ue = /* @__PURE__ */ f.createElement(ft, {
    className: `${Q}-presets`
  }, S && /* @__PURE__ */ f.createElement(Yr, null), p ? /* @__PURE__ */ f.createElement(qr, null) : /* @__PURE__ */ f.createElement(Kr, null));
  typeof b == "function" ? ue = b(ue, {
    components: rr
  }) : (b || b === !1) && (ue = b);
  const Me = {
    prefixCls: z,
    onSend: pe,
    onSendDisabled: !te,
    onClear: se,
    onClearDisabled: !te,
    onCancel: g,
    onCancelDisabled: !p,
    onSpeech: () => L(!1),
    onSpeechDisabled: !B,
    speechRecording: j,
    disabled: E
  }, Pe = typeof T == "function" ? T({
    components: rr
  }) : T || null;
  return le(/* @__PURE__ */ f.createElement("div", {
    ref: U,
    className: V,
    style: {
      ...I.style,
      ...a
    }
  }, R && /* @__PURE__ */ f.createElement(Gr.Provider, {
    value: {
      prefixCls: A
    }
  }, R), /* @__PURE__ */ f.createElement(Ot.Provider, {
    value: Me
  }, /* @__PURE__ */ f.createElement("div", {
    className: K(`${A}-content`, I.classNames.content, i.content),
    style: {
      ...I.styles.content,
      ...r.content
    },
    onMouseDown: oe
  }, x && /* @__PURE__ */ f.createElement("div", {
    className: K(`${A}-prefix`, I.classNames.prefix, i.prefix),
    style: {
      ...I.styles.prefix,
      ...r.prefix
    }
  }, x), /* @__PURE__ */ f.createElement(ne, ve({}, re, {
    disabled: E,
    style: {
      ...I.styles.input,
      ...r.input
    },
    className: K(y, I.classNames.input, i.input),
    autoSize: M,
    value: te,
    onChange: (Z) => {
      Se(Z.target.value, Z), L(!0);
    },
    onPressEnter: G,
    onCompositionStart: me,
    onCompositionEnd: ye,
    onKeyDown: C,
    onPaste: ie,
    variant: "borderless",
    readOnly: u
  })), ue && /* @__PURE__ */ f.createElement("div", {
    className: K(Q, I.classNames.actions, i.actions),
    style: {
      ...I.styles.actions,
      ...r.actions
    }
  }, ue)), Pe && /* @__PURE__ */ f.createElement("div", {
    className: K(`${A}-footer`, I.classNames.footer, i.footer),
    style: {
      ...I.styles.footer,
      ...r.footer
    }
  }, Pe))));
}), ln = Ba;
ln.Header = Ra;
function Ha(n) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(n.trim());
}
function za(n, e = !1) {
  try {
    if (pi(n))
      return n;
    if (e && !Ha(n))
      return;
    if (typeof n == "string") {
      let t = n.trim();
      return t.startsWith(";") && (t = t.slice(1)), t.endsWith(";") && (t = t.slice(0, -1)), new Function(`return (...args) => (${t})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function ir(n, e) {
  return qt(() => za(n, e), [n, e]);
}
function ct(n) {
  const e = he(n);
  return e.current = n, ci((...t) => {
    var r;
    return (r = e.current) == null ? void 0 : r.call(e, ...t);
  }, []);
}
function Ua({
  value: n,
  onValueChange: e
}) {
  const [t, r] = $e(n), i = he(e);
  i.current = e;
  const o = he(t);
  return o.current = t, Ce(() => {
    i.current(t);
  }, [t]), Ce(() => {
    oo(n, o.current) || r(n);
  }, [n]), [t, r];
}
function Va(n, e) {
  return Object.keys(n).reduce((t, r) => (n[r] !== void 0 && n[r] !== null && (t[r] = n[r]), t), {});
}
function Ut(n, e, t, r) {
  return new (t || (t = Promise))(function(i, o) {
    function s(l) {
      try {
        c(r.next(l));
      } catch (u) {
        o(u);
      }
    }
    function a(l) {
      try {
        c(r.throw(l));
      } catch (u) {
        o(u);
      }
    }
    function c(l) {
      var u;
      l.done ? i(l.value) : (u = l.value, u instanceof t ? u : new t(function(d) {
        d(u);
      })).then(s, a);
    }
    c((r = r.apply(n, [])).next());
  });
}
class Zr {
  constructor() {
    this.listeners = {};
  }
  on(e, t, r) {
    if (this.listeners[e] || (this.listeners[e] = /* @__PURE__ */ new Set()), r == null ? void 0 : r.once) {
      const i = (...o) => {
        this.un(e, i), t(...o);
      };
      return this.listeners[e].add(i), () => this.un(e, i);
    }
    return this.listeners[e].add(t), () => this.un(e, t);
  }
  un(e, t) {
    var r;
    (r = this.listeners[e]) === null || r === void 0 || r.delete(t);
  }
  once(e, t) {
    return this.on(e, t, {
      once: !0
    });
  }
  unAll() {
    this.listeners = {};
  }
  emit(e, ...t) {
    this.listeners[e] && this.listeners[e].forEach((r) => r(...t));
  }
}
class Xa extends Zr {
  constructor(e) {
    super(), this.subscriptions = [], this.isDestroyed = !1, this.options = e;
  }
  onInit() {
  }
  _init(e) {
    this.isDestroyed && (this.subscriptions = [], this.isDestroyed = !1), this.wavesurfer = e, this.onInit();
  }
  destroy() {
    this.emit("destroy"), this.subscriptions.forEach((e) => e()), this.subscriptions = [], this.isDestroyed = !0, this.wavesurfer = void 0;
  }
}
class Ga extends Zr {
  constructor() {
    super(...arguments), this.animationFrameId = null, this.isRunning = !1;
  }
  start() {
    if (this.isRunning) return;
    this.isRunning = !0;
    const e = () => {
      this.isRunning && (this.emit("tick"), this.animationFrameId = requestAnimationFrame(e));
    };
    e();
  }
  stop() {
    this.isRunning = !1, this.animationFrameId !== null && (cancelAnimationFrame(this.animationFrameId), this.animationFrameId = null);
  }
  destroy() {
    this.stop();
  }
}
const qa = ["audio/webm", "audio/wav", "audio/mpeg", "audio/mp4", "audio/mp3"];
class pn extends Xa {
  constructor(e) {
    var t, r, i, o, s, a;
    super(Object.assign(Object.assign({}, e), {
      audioBitsPerSecond: (t = e.audioBitsPerSecond) !== null && t !== void 0 ? t : 128e3,
      scrollingWaveform: (r = e.scrollingWaveform) !== null && r !== void 0 && r,
      scrollingWaveformWindow: (i = e.scrollingWaveformWindow) !== null && i !== void 0 ? i : 5,
      continuousWaveform: (o = e.continuousWaveform) !== null && o !== void 0 && o,
      renderRecordedAudio: (s = e.renderRecordedAudio) === null || s === void 0 || s,
      mediaRecorderTimeslice: (a = e.mediaRecorderTimeslice) !== null && a !== void 0 ? a : void 0
    })), this.stream = null, this.mediaRecorder = null, this.dataWindow = null, this.isWaveformPaused = !1, this.lastStartTime = 0, this.lastDuration = 0, this.duration = 0, this.micStream = null, this.recordedBlobUrl = null, this.timer = new Ga(), this.subscriptions.push(this.timer.on("tick", () => {
      const c = performance.now() - this.lastStartTime;
      this.duration = this.isPaused() ? this.duration : this.lastDuration + c, this.emit("record-progress", this.duration);
    }));
  }
  static create(e) {
    return new pn(e || {});
  }
  renderMicStream(e) {
    var t;
    const r = new AudioContext(), i = r.createMediaStreamSource(e), o = r.createAnalyser();
    i.connect(o), this.options.continuousWaveform && (o.fftSize = 32);
    const s = o.frequencyBinCount, a = new Float32Array(s);
    let c = 0;
    this.wavesurfer && ((t = this.originalOptions) !== null && t !== void 0 || (this.originalOptions = Object.assign({}, this.wavesurfer.options)), this.wavesurfer.options.interact = !1, this.options.scrollingWaveform && (this.wavesurfer.options.cursorWidth = 0));
    const l = setInterval(() => {
      var u, d, h, p;
      if (!this.isWaveformPaused) {
        if (o.getFloatTimeDomainData(a), this.options.scrollingWaveform) {
          const v = Math.floor((this.options.scrollingWaveformWindow || 0) * r.sampleRate), g = Math.min(v, this.dataWindow ? this.dataWindow.length + s : s), m = new Float32Array(v);
          if (this.dataWindow) {
            const b = Math.max(0, v - this.dataWindow.length);
            m.set(this.dataWindow.slice(-g + s), b);
          }
          m.set(a, v - s), this.dataWindow = m;
        } else if (this.options.continuousWaveform) {
          if (!this.dataWindow) {
            const g = this.options.continuousWaveformDuration ? Math.round(100 * this.options.continuousWaveformDuration) : ((d = (u = this.wavesurfer) === null || u === void 0 ? void 0 : u.getWidth()) !== null && d !== void 0 ? d : 0) * window.devicePixelRatio;
            this.dataWindow = new Float32Array(g);
          }
          let v = 0;
          for (let g = 0; g < s; g++) {
            const m = Math.abs(a[g]);
            m > v && (v = m);
          }
          if (c + 1 > this.dataWindow.length) {
            const g = new Float32Array(2 * this.dataWindow.length);
            g.set(this.dataWindow, 0), this.dataWindow = g;
          }
          this.dataWindow[c] = v, c++;
        } else this.dataWindow = a;
        if (this.wavesurfer) {
          const v = ((p = (h = this.dataWindow) === null || h === void 0 ? void 0 : h.length) !== null && p !== void 0 ? p : 0) / 100;
          this.wavesurfer.load("", [this.dataWindow], this.options.scrollingWaveform ? this.options.scrollingWaveformWindow : v).then(() => {
            this.wavesurfer && this.options.continuousWaveform && (this.wavesurfer.setTime(this.getDuration() / 1e3), this.wavesurfer.options.minPxPerSec || this.wavesurfer.setOptions({
              minPxPerSec: this.wavesurfer.getWidth() / this.wavesurfer.getDuration()
            }));
          }).catch((g) => {
            console.error("Error rendering real-time recording data:", g);
          });
        }
      }
    }, 10);
    return {
      onDestroy: () => {
        clearInterval(l), i == null || i.disconnect(), r == null || r.close();
      },
      onEnd: () => {
        this.isWaveformPaused = !0, this.stopMic();
      }
    };
  }
  startMic(e) {
    return Ut(this, void 0, void 0, function* () {
      let t;
      this.micStream && this.stopMic();
      try {
        t = yield navigator.mediaDevices.getUserMedia({
          audio: e == null || e
        });
      } catch (i) {
        throw new Error("Error accessing the microphone: " + i.message);
      }
      const r = this.renderMicStream(t);
      return this.micStream = r, this.unsubscribeDestroy = this.once("destroy", r.onDestroy), this.unsubscribeRecordEnd = this.once("record-end", r.onEnd), this.stream = t, t;
    });
  }
  stopMic() {
    var e, t, r;
    (e = this.micStream) === null || e === void 0 || e.onDestroy(), (t = this.unsubscribeDestroy) === null || t === void 0 || t.call(this), (r = this.unsubscribeRecordEnd) === null || r === void 0 || r.call(this), this.micStream = null, this.unsubscribeDestroy = void 0, this.unsubscribeRecordEnd = void 0, this.stream && (this.stream.getTracks().forEach((i) => i.stop()), this.stream = null, this.mediaRecorder = null);
  }
  startRecording(e) {
    return Ut(this, void 0, void 0, function* () {
      const t = this.stream || (yield this.startMic(e));
      this.dataWindow = null;
      const r = this.mediaRecorder || new MediaRecorder(t, {
        mimeType: this.options.mimeType || qa.find((s) => MediaRecorder.isTypeSupported(s)),
        audioBitsPerSecond: this.options.audioBitsPerSecond
      });
      this.mediaRecorder = r, this.stopRecording();
      const i = [];
      r.ondataavailable = (s) => {
        s.data.size > 0 && i.push(s.data), this.emit("record-data-available", s.data);
      };
      const o = (s) => {
        var a;
        const c = new Blob(i, {
          type: r.mimeType
        });
        this.emit(s, c), this.options.renderRecordedAudio && (this.applyOriginalOptionsIfNeeded(), this.recordedBlobUrl && URL.revokeObjectURL(this.recordedBlobUrl), this.recordedBlobUrl = URL.createObjectURL(c), (a = this.wavesurfer) === null || a === void 0 || a.load(this.recordedBlobUrl));
      };
      r.onpause = () => o("record-pause"), r.onstop = () => o("record-end"), r.start(this.options.mediaRecorderTimeslice), this.lastStartTime = performance.now(), this.lastDuration = 0, this.duration = 0, this.isWaveformPaused = !1, this.timer.start(), this.emit("record-start");
    });
  }
  getDuration() {
    return this.duration;
  }
  isRecording() {
    var e;
    return ((e = this.mediaRecorder) === null || e === void 0 ? void 0 : e.state) === "recording";
  }
  isPaused() {
    var e;
    return ((e = this.mediaRecorder) === null || e === void 0 ? void 0 : e.state) === "paused";
  }
  isActive() {
    var e;
    return ((e = this.mediaRecorder) === null || e === void 0 ? void 0 : e.state) !== "inactive";
  }
  stopRecording() {
    var e;
    this.isActive() && ((e = this.mediaRecorder) === null || e === void 0 || e.stop(), this.timer.stop());
  }
  pauseRecording() {
    var e, t;
    this.isRecording() && (this.isWaveformPaused = !0, (e = this.mediaRecorder) === null || e === void 0 || e.requestData(), (t = this.mediaRecorder) === null || t === void 0 || t.pause(), this.timer.stop(), this.lastDuration = this.duration);
  }
  resumeRecording() {
    var e;
    this.isPaused() && (this.isWaveformPaused = !1, (e = this.mediaRecorder) === null || e === void 0 || e.resume(), this.timer.start(), this.lastStartTime = performance.now(), this.emit("record-resume"));
  }
  static getAvailableAudioDevices() {
    return Ut(this, void 0, void 0, function* () {
      return navigator.mediaDevices.enumerateDevices().then((e) => e.filter((t) => t.kind === "audioinput"));
    });
  }
  destroy() {
    this.applyOriginalOptionsIfNeeded(), super.destroy(), this.stopRecording(), this.stopMic(), this.recordedBlobUrl && (URL.revokeObjectURL(this.recordedBlobUrl), this.recordedBlobUrl = null);
  }
  applyOriginalOptionsIfNeeded() {
    this.wavesurfer && this.originalOptions && (this.wavesurfer.setOptions(this.originalOptions), delete this.originalOptions);
  }
}
class Ge {
  constructor() {
    this.listeners = {};
  }
  /** Subscribe to an event. Returns an unsubscribe function. */
  on(e, t, r) {
    if (this.listeners[e] || (this.listeners[e] = /* @__PURE__ */ new Set()), r != null && r.once) {
      const i = (...o) => {
        this.un(e, i), t(...o);
      };
      return this.listeners[e].add(i), () => this.un(e, i);
    }
    return this.listeners[e].add(t), () => this.un(e, t);
  }
  /** Unsubscribe from an event */
  un(e, t) {
    var r;
    (r = this.listeners[e]) === null || r === void 0 || r.delete(t);
  }
  /** Subscribe to an event only once */
  once(e, t) {
    return this.on(e, t, {
      once: !0
    });
  }
  /** Clear all events */
  unAll() {
    this.listeners = {};
  }
  /** Emit an event */
  emit(e, ...t) {
    this.listeners[e] && this.listeners[e].forEach((r) => r(...t));
  }
}
class Ka extends Ge {
  /** Create a plugin instance */
  constructor(e) {
    super(), this.subscriptions = [], this.isDestroyed = !1, this.options = e;
  }
  /** Called after this.wavesurfer is available */
  onInit() {
  }
  /** Do not call directly, only called by WavesSurfer internally */
  _init(e) {
    this.isDestroyed && (this.subscriptions = [], this.isDestroyed = !1), this.wavesurfer = e, this.onInit();
  }
  /** Destroy the plugin and unsubscribe from all events */
  destroy() {
    this.emit("destroy"), this.subscriptions.forEach((e) => e()), this.subscriptions = [], this.isDestroyed = !0, this.wavesurfer = void 0;
  }
}
var Ya = function(n, e, t, r) {
  function i(o) {
    return o instanceof t ? o : new t(function(s) {
      s(o);
    });
  }
  return new (t || (t = Promise))(function(o, s) {
    function a(u) {
      try {
        l(r.next(u));
      } catch (d) {
        s(d);
      }
    }
    function c(u) {
      try {
        l(r.throw(u));
      } catch (d) {
        s(d);
      }
    }
    function l(u) {
      u.done ? o(u.value) : i(u.value).then(a, c);
    }
    l((r = r.apply(n, e || [])).next());
  });
};
function Za(n, e) {
  return Ya(this, void 0, void 0, function* () {
    const t = new AudioContext({
      sampleRate: e
    });
    try {
      return yield t.decodeAudioData(n);
    } finally {
      t.close();
    }
  });
}
function Qa(n) {
  const e = n[0];
  if (e.some((t) => t > 1 || t < -1)) {
    const t = e.length;
    let r = 0;
    for (let i = 0; i < t; i++) {
      const o = Math.abs(e[i]);
      o > r && (r = o);
    }
    for (const i of n)
      for (let o = 0; o < t; o++)
        i[o] /= r;
  }
  return n;
}
function Ja(n, e) {
  if (!n || n.length === 0)
    throw new Error("channelData must be a non-empty array");
  if (e <= 0)
    throw new Error("duration must be greater than 0");
  if (typeof n[0] == "number" && (n = [n]), !n[0] || n[0].length === 0)
    throw new Error("channelData must contain non-empty channel arrays");
  Qa(n);
  const t = n.map((r) => r instanceof Float32Array ? r : Float32Array.from(r));
  return {
    duration: e,
    length: t[0].length,
    sampleRate: t[0].length / e,
    numberOfChannels: t.length,
    getChannelData: (r) => {
      const i = t[r];
      if (!i)
        throw new Error(`Channel ${r} not found`);
      return i;
    },
    copyFromChannel: AudioBuffer.prototype.copyFromChannel,
    copyToChannel: AudioBuffer.prototype.copyToChannel
  };
}
const rt = {
  decode: Za,
  createBuffer: Ja
};
function Qr(n, e) {
  const t = e.xmlns ? document.createElementNS(e.xmlns, n) : document.createElement(n);
  for (const [r, i] of Object.entries(e))
    if (r === "children" && i)
      for (const [o, s] of Object.entries(i))
        s instanceof Node ? t.appendChild(s) : typeof s == "string" ? t.appendChild(document.createTextNode(s)) : t.appendChild(Qr(o, s));
    else r === "style" ? Object.assign(t.style, i) : r === "textContent" ? t.textContent = i : t.setAttribute(r, i.toString());
  return t;
}
function or(n, e, t) {
  const r = Qr(n, e || {});
  return t == null || t.appendChild(r), r;
}
const el = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  createElement: or,
  default: or
}, Symbol.toStringTag, {
  value: "Module"
}));
var Jr = function(n, e, t, r) {
  function i(o) {
    return o instanceof t ? o : new t(function(s) {
      s(o);
    });
  }
  return new (t || (t = Promise))(function(o, s) {
    function a(u) {
      try {
        l(r.next(u));
      } catch (d) {
        s(d);
      }
    }
    function c(u) {
      try {
        l(r.throw(u));
      } catch (d) {
        s(d);
      }
    }
    function l(u) {
      u.done ? o(u.value) : i(u.value).then(a, c);
    }
    l((r = r.apply(n, e || [])).next());
  });
};
function tl(n, e) {
  return Jr(this, void 0, void 0, function* () {
    if (!n.body || !n.headers) return;
    const t = n.body.getReader(), r = Number(n.headers.get("Content-Length")) || 0;
    let i = 0;
    const o = (s) => {
      i += (s == null ? void 0 : s.length) || 0;
      const a = Math.round(i / r * 100);
      e(a);
    };
    try {
      for (; ; ) {
        const s = yield t.read();
        if (s.done)
          break;
        o(s.value);
      }
    } catch (s) {
      console.warn("Progress tracking error:", s);
    }
  });
}
function nl(n, e, t) {
  return Jr(this, void 0, void 0, function* () {
    const r = yield fetch(n, t);
    if (r.status >= 400)
      throw new Error(`Failed to fetch ${n}: ${r.status} (${r.statusText})`);
    return tl(r.clone(), e), r.blob();
  });
}
const rl = {
  fetchBlob: nl
};
var il = function(n, e, t, r) {
  function i(o) {
    return o instanceof t ? o : new t(function(s) {
      s(o);
    });
  }
  return new (t || (t = Promise))(function(o, s) {
    function a(u) {
      try {
        l(r.next(u));
      } catch (d) {
        s(d);
      }
    }
    function c(u) {
      try {
        l(r.throw(u));
      } catch (d) {
        s(d);
      }
    }
    function l(u) {
      u.done ? o(u.value) : i(u.value).then(a, c);
    }
    l((r = r.apply(n, e || [])).next());
  });
};
class ol extends Ge {
  constructor(e) {
    super(), this.isExternalMedia = !1, e.media ? (this.media = e.media, this.isExternalMedia = !0) : this.media = document.createElement("audio"), e.mediaControls && (this.media.controls = !0), e.autoplay && (this.media.autoplay = !0), e.playbackRate != null && this.onMediaEvent("canplay", () => {
      e.playbackRate != null && (this.media.playbackRate = e.playbackRate);
    }, {
      once: !0
    });
  }
  onMediaEvent(e, t, r) {
    return this.media.addEventListener(e, t, r), () => this.media.removeEventListener(e, t, r);
  }
  getSrc() {
    return this.media.currentSrc || this.media.src || "";
  }
  revokeSrc() {
    const e = this.getSrc();
    e.startsWith("blob:") && URL.revokeObjectURL(e);
  }
  canPlayType(e) {
    return this.media.canPlayType(e) !== "";
  }
  setSrc(e, t) {
    const r = this.getSrc();
    if (e && r === e) return;
    this.revokeSrc();
    const i = t instanceof Blob && (this.canPlayType(t.type) || !e) ? URL.createObjectURL(t) : e;
    if (r && this.media.removeAttribute("src"), i || e)
      try {
        this.media.src = i;
      } catch {
        this.media.src = e;
      }
  }
  destroy() {
    this.isExternalMedia || (this.media.pause(), this.revokeSrc(), this.media.removeAttribute("src"), this.media.load(), this.media.remove());
  }
  setMediaElement(e) {
    this.media = e;
  }
  /** Start playing the audio */
  play() {
    return il(this, void 0, void 0, function* () {
      try {
        return yield this.media.play();
      } catch (e) {
        if (e instanceof DOMException && e.name === "AbortError")
          return;
        throw e;
      }
    });
  }
  /** Pause the audio */
  pause() {
    this.media.pause();
  }
  /** Check if the audio is playing */
  isPlaying() {
    return !this.media.paused && !this.media.ended;
  }
  /** Jump to a specific time in the audio (in seconds) */
  setTime(e) {
    this.media.currentTime = Math.max(0, Math.min(e, this.getDuration()));
  }
  /** Get the duration of the audio in seconds */
  getDuration() {
    return this.media.duration;
  }
  /** Get the current audio position in seconds */
  getCurrentTime() {
    return this.media.currentTime;
  }
  /** Get the audio volume */
  getVolume() {
    return this.media.volume;
  }
  /** Set the audio volume */
  setVolume(e) {
    this.media.volume = e;
  }
  /** Get the audio muted state */
  getMuted() {
    return this.media.muted;
  }
  /** Mute or unmute the audio */
  setMuted(e) {
    this.media.muted = e;
  }
  /** Get the playback speed */
  getPlaybackRate() {
    return this.media.playbackRate;
  }
  /** Check if the audio is seeking */
  isSeeking() {
    return this.media.seeking;
  }
  /** Set the playback speed, pass an optional false to NOT preserve the pitch */
  setPlaybackRate(e, t) {
    t != null && (this.media.preservesPitch = t), this.media.playbackRate = e;
  }
  /** Get the HTML media element */
  getMediaElement() {
    return this.media;
  }
  /** Set a sink id to change the audio output device */
  setSinkId(e) {
    return this.media.setSinkId(e);
  }
}
function sl(n, e, t, r, i = 3, o = 0, s = 100) {
  if (!n) return () => {
  };
  const a = /* @__PURE__ */ new Map(), c = matchMedia("(pointer: coarse)").matches;
  let l = () => {
  };
  const u = (d) => {
    if (d.button !== o || (a.set(d.pointerId, d), a.size > 1))
      return;
    let h = d.clientX, p = d.clientY, v = !1;
    const g = Date.now(), m = (S) => {
      if (S.defaultPrevented || a.size > 1 || c && Date.now() - g < s) return;
      const x = S.clientX, T = S.clientY, R = x - h, O = T - p;
      if (v || Math.abs(R) > i || Math.abs(O) > i) {
        S.preventDefault(), S.stopPropagation();
        const P = n.getBoundingClientRect(), {
          left: M,
          top: $
        } = P;
        v || (t == null || t(h - M, p - $), v = !0), e(R, O, x - M, T - $), h = x, p = T;
      }
    }, b = (S) => {
      if (a.delete(S.pointerId), v) {
        const x = S.clientX, T = S.clientY, R = n.getBoundingClientRect(), {
          left: O,
          top: P
        } = R;
        r == null || r(x - O, T - P);
      }
      l();
    }, w = (S) => {
      a.delete(S.pointerId), (!S.relatedTarget || S.relatedTarget === document.documentElement) && b(S);
    }, C = (S) => {
      v && (S.stopPropagation(), S.preventDefault());
    }, E = (S) => {
      S.defaultPrevented || a.size > 1 || v && S.preventDefault();
    };
    document.addEventListener("pointermove", m), document.addEventListener("pointerup", b), document.addEventListener("pointerout", w), document.addEventListener("pointercancel", w), document.addEventListener("touchmove", E, {
      passive: !1
    }), document.addEventListener("click", C, {
      capture: !0
    }), l = () => {
      document.removeEventListener("pointermove", m), document.removeEventListener("pointerup", b), document.removeEventListener("pointerout", w), document.removeEventListener("pointercancel", w), document.removeEventListener("touchmove", E), setTimeout(() => {
        document.removeEventListener("click", C, {
          capture: !0
        });
      }, 10);
    };
  };
  return n.addEventListener("pointerdown", u), () => {
    l(), n.removeEventListener("pointerdown", u), a.clear();
  };
}
const ei = 128, al = 8e3, ll = 10;
function Vt(n) {
  return n < 0 ? 0 : n > 1 ? 1 : n;
}
function cl({
  width: n,
  height: e,
  length: t,
  options: r,
  pixelRatio: i
}) {
  const o = e / 2, s = r.barWidth ? r.barWidth * i : 1, a = r.barGap ? r.barGap * i : r.barWidth ? s / 2 : 0, c = r.barRadius || 0, l = s + a || 1, u = t > 0 ? n / l / t : 0;
  return {
    halfHeight: o,
    barWidth: s,
    barGap: a,
    barRadius: c,
    barIndexScale: u,
    barSpacing: l
  };
}
function ul({
  maxTop: n,
  maxBottom: e,
  halfHeight: t,
  vScale: r
}) {
  const i = Math.round(n * t * r), o = Math.round(e * t * r), s = i + o || 1;
  return {
    topHeight: i,
    totalHeight: s
  };
}
function dl({
  barAlign: n,
  halfHeight: e,
  topHeight: t,
  totalHeight: r,
  canvasHeight: i
}) {
  return n === "top" ? 0 : n === "bottom" ? i - r : e - t;
}
function fl({
  channelData: n,
  barIndexScale: e,
  barSpacing: t,
  barWidth: r,
  halfHeight: i,
  vScale: o,
  canvasHeight: s,
  barAlign: a
}) {
  const c = n[0] || [], l = n[1] || c, u = c.length, d = [];
  let h = 0, p = 0, v = 0;
  for (let g = 0; g <= u; g++) {
    const m = Math.round(g * e);
    if (m > h) {
      const {
        topHeight: C,
        totalHeight: E
      } = ul({
        maxTop: p,
        maxBottom: v,
        halfHeight: i,
        vScale: o
      }), S = dl({
        barAlign: a,
        halfHeight: i,
        topHeight: C,
        totalHeight: E,
        canvasHeight: s
      });
      d.push({
        x: h * t,
        y: S,
        width: r,
        height: E
      }), h = m, p = 0, v = 0;
    }
    const b = Math.abs(c[g] || 0), w = Math.abs(l[g] || 0);
    b > p && (p = b), w > v && (v = w);
  }
  return d;
}
function sr(n, e, t) {
  const r = e - n.left, i = t - n.top, o = r / n.width, s = i / n.height;
  return [o, s];
}
function hl({
  optionsHeight: n,
  optionsSplitChannels: e,
  parentHeight: t,
  numberOfChannels: r,
  defaultHeight: i = ei
}) {
  if (n == null) return i;
  const o = Number(n);
  if (!isNaN(o)) return o;
  if (n === "auto") {
    const s = t || i;
    return e != null && e.every((a) => !a.overlay) ? s / r : s;
  }
  return i;
}
function pl(n) {
  return Math.max(1, n || 1);
}
function ti(n) {
  return !!(n.barWidth || n.barGap || n.barAlign);
}
function ml(n, e) {
  if (!Array.isArray(n)) return n || "";
  if (n.length === 0) return "#999";
  if (n.length < 2) return n[0] || "";
  const t = document.createElement("canvas"), r = t.getContext("2d"), i = t.height * e, o = r.createLinearGradient(0, 0, 0, i || e), s = 1 / (n.length - 1);
  return n.forEach((a, c) => {
    o.addColorStop(c * s, a);
  }), o;
}
function gl({
  duration: n,
  minPxPerSec: e = 0,
  parentWidth: t,
  fillParent: r,
  pixelRatio: i
}) {
  const o = Math.ceil(n * e), s = o > t, a = !!(r && !s), c = (a ? t : o) * i;
  return {
    scrollWidth: o,
    isScrollable: s,
    useParentWidth: a,
    width: c
  };
}
function ni(n, e) {
  if (!ti(e)) return n;
  const t = e.barWidth || 0.5, r = e.barGap || t / 2, i = t + r;
  return i === 0 ? n : Math.floor(n / i) * i;
}
function vl({
  clientWidth: n,
  totalWidth: e,
  options: t
}) {
  const r = Math.min(al, n, e);
  return ni(r, t);
}
function bl({
  channelData: n,
  offset: e,
  clampedWidth: t,
  totalWidth: r
}) {
  return n.map((i) => {
    const o = Math.floor(e / r * i.length), s = Math.floor((e + t) / r * i.length);
    return i.slice(o, s);
  });
}
function yl(n) {
  return n > ll;
}
function ar({
  scrollLeft: n,
  totalWidth: e,
  numCanvases: t
}) {
  if (e === 0) return [0];
  const r = n / e, i = Math.floor(r * t);
  return [i - 1, i, i + 1];
}
function wl({
  channelData: n,
  barHeight: e,
  normalize: t
}) {
  var r;
  const i = e || 1;
  if (!t) return i;
  const o = n[0];
  if (!o || o.length === 0) return i;
  let s = 0;
  for (let a = 0; a < o.length; a++) {
    const c = (r = o[a]) !== null && r !== void 0 ? r : 0, l = Math.abs(c);
    l > s && (s = l);
  }
  return s ? i / s : i;
}
function Sl({
  channelData: n,
  width: e,
  height: t,
  vScale: r
}) {
  const i = t / 2, o = n[0] || [], s = n[1] || o;
  return [o, s].map((c, l) => {
    const u = c.length, d = u ? e / u : 0, h = i, p = l === 0 ? -1 : 1, v = [{
      x: 0,
      y: h
    }];
    let g = 0, m = 0;
    for (let b = 0; b <= u; b++) {
      const w = Math.round(b * d);
      if (w > g) {
        const E = Math.round(m * i * r) || 1, S = h + E * p;
        v.push({
          x: g,
          y: S
        }), g = w, m = 0;
      }
      const C = Math.abs(c[b] || 0);
      C > m && (m = C);
    }
    return v.push({
      x: g,
      y: h
    }), v;
  });
}
function lr({
  scrollLeft: n,
  clientWidth: e,
  scrollWidth: t
}) {
  if (t === 0)
    return {
      startX: 0,
      endX: 0
    };
  const r = n / t, i = (n + e) / t;
  return {
    startX: r,
    endX: i
  };
}
function xl(n) {
  const e = n * 2;
  return (e < 0 ? Math.floor(e) : Math.ceil(e)) / 2;
}
var cr = function(n, e, t, r) {
  function i(o) {
    return o instanceof t ? o : new t(function(s) {
      s(o);
    });
  }
  return new (t || (t = Promise))(function(o, s) {
    function a(u) {
      try {
        l(r.next(u));
      } catch (d) {
        s(d);
      }
    }
    function c(u) {
      try {
        l(r.throw(u));
      } catch (d) {
        s(d);
      }
    }
    function l(u) {
      u.done ? o(u.value) : i(u.value).then(a, c);
    }
    l((r = r.apply(n, e || [])).next());
  });
}, Cl = function(n, e) {
  var t = {};
  for (var r in n) Object.prototype.hasOwnProperty.call(n, r) && e.indexOf(r) < 0 && (t[r] = n[r]);
  if (n != null && typeof Object.getOwnPropertySymbols == "function") for (var i = 0, r = Object.getOwnPropertySymbols(n); i < r.length; i++)
    e.indexOf(r[i]) < 0 && Object.prototype.propertyIsEnumerable.call(n, r[i]) && (t[r[i]] = n[r[i]]);
  return t;
};
class El extends Ge {
  constructor(e, t) {
    super(), this.timeouts = [], this.isScrollable = !1, this.audioData = null, this.resizeObserver = null, this.lastContainerWidth = 0, this.isDragging = !1, this.subscriptions = [], this.unsubscribeOnScroll = [], this.dragUnsubscribe = null, this.subscriptions = [], this.options = e;
    const r = this.parentFromOptionsContainer(e.container);
    this.parent = r;
    const [i, o] = this.initHtml();
    r.appendChild(i), this.container = i, this.scrollContainer = o.querySelector(".scroll"), this.wrapper = o.querySelector(".wrapper"), this.canvasWrapper = o.querySelector(".canvases"), this.progressWrapper = o.querySelector(".progress"), this.cursor = o.querySelector(".cursor"), t && o.appendChild(t), this.initEvents();
  }
  parentFromOptionsContainer(e) {
    let t;
    if (typeof e == "string" ? t = document.querySelector(e) : e instanceof HTMLElement && (t = e), !t)
      throw new Error("Container not found");
    return t;
  }
  initEvents() {
    if (this.wrapper.addEventListener("click", (e) => {
      const t = this.wrapper.getBoundingClientRect(), [r, i] = sr(t, e.clientX, e.clientY);
      this.emit("click", r, i);
    }), this.wrapper.addEventListener("dblclick", (e) => {
      const t = this.wrapper.getBoundingClientRect(), [r, i] = sr(t, e.clientX, e.clientY);
      this.emit("dblclick", r, i);
    }), (this.options.dragToSeek === !0 || typeof this.options.dragToSeek == "object") && this.initDrag(), this.scrollContainer.addEventListener("scroll", () => {
      const {
        scrollLeft: e,
        scrollWidth: t,
        clientWidth: r
      } = this.scrollContainer, {
        startX: i,
        endX: o
      } = lr({
        scrollLeft: e,
        scrollWidth: t,
        clientWidth: r
      });
      this.emit("scroll", i, o, e, e + r);
    }), typeof ResizeObserver == "function") {
      const e = this.createDelay(100);
      this.resizeObserver = new ResizeObserver(() => {
        e().then(() => this.onContainerResize()).catch(() => {
        });
      }), this.resizeObserver.observe(this.scrollContainer);
    }
  }
  onContainerResize() {
    const e = this.parent.clientWidth;
    e === this.lastContainerWidth && this.options.height !== "auto" || (this.lastContainerWidth = e, this.reRender(), this.emit("resize"));
  }
  initDrag() {
    this.dragUnsubscribe || (this.dragUnsubscribe = sl(
      this.wrapper,
      // On drag
      (e, t, r) => {
        const i = this.wrapper.getBoundingClientRect().width;
        this.emit("drag", Vt(r / i));
      },
      // On start drag
      (e) => {
        this.isDragging = !0;
        const t = this.wrapper.getBoundingClientRect().width;
        this.emit("dragstart", Vt(e / t));
      },
      // On end drag
      (e) => {
        this.isDragging = !1;
        const t = this.wrapper.getBoundingClientRect().width;
        this.emit("dragend", Vt(e / t));
      }
    ), this.subscriptions.push(this.dragUnsubscribe));
  }
  initHtml() {
    const e = document.createElement("div"), t = e.attachShadow({
      mode: "open"
    }), r = this.options.cspNonce && typeof this.options.cspNonce == "string" ? this.options.cspNonce.replace(/"/g, "") : "";
    return t.innerHTML = `
      <style${r ? ` nonce="${r}"` : ""}>
        :host {
          user-select: none;
          min-width: 1px;
        }
        :host audio {
          display: block;
          width: 100%;
        }
        :host .scroll {
          overflow-x: auto;
          overflow-y: hidden;
          width: 100%;
          position: relative;
        }
        :host .noScrollbar {
          scrollbar-color: transparent;
          scrollbar-width: none;
        }
        :host .noScrollbar::-webkit-scrollbar {
          display: none;
          -webkit-appearance: none;
        }
        :host .wrapper {
          position: relative;
          overflow: visible;
          z-index: 2;
        }
        :host .canvases {
          min-height: ${this.getHeight(this.options.height, this.options.splitChannels)}px;
          pointer-events: none;
        }
        :host .canvases > div {
          position: relative;
        }
        :host canvas {
          display: block;
          position: absolute;
          top: 0;
          image-rendering: pixelated;
        }
        :host .progress {
          pointer-events: none;
          position: absolute;
          z-index: 2;
          top: 0;
          left: 0;
          width: 0;
          height: 100%;
          overflow: hidden;
        }
        :host .progress > div {
          position: relative;
        }
        :host .cursor {
          pointer-events: none;
          position: absolute;
          z-index: 5;
          top: 0;
          left: 0;
          height: 100%;
          border-radius: 2px;
        }
      </style>

      <div class="scroll" part="scroll">
        <div class="wrapper" part="wrapper">
          <div class="canvases" part="canvases"></div>
          <div class="progress" part="progress"></div>
          <div class="cursor" part="cursor"></div>
        </div>
      </div>
    `, [e, t];
  }
  /** Wavesurfer itself calls this method. Do not call it manually. */
  setOptions(e) {
    if (this.options.container !== e.container) {
      const t = this.parentFromOptionsContainer(e.container);
      t.appendChild(this.container), this.parent = t;
    }
    (e.dragToSeek === !0 || typeof this.options.dragToSeek == "object") && this.initDrag(), this.options = e, this.reRender();
  }
  getWrapper() {
    return this.wrapper;
  }
  getWidth() {
    return this.scrollContainer.clientWidth;
  }
  getScroll() {
    return this.scrollContainer.scrollLeft;
  }
  setScroll(e) {
    this.scrollContainer.scrollLeft = e;
  }
  setScrollPercentage(e) {
    const {
      scrollWidth: t
    } = this.scrollContainer, r = t * e;
    this.setScroll(r);
  }
  destroy() {
    var e;
    this.subscriptions.forEach((t) => t()), this.container.remove(), this.resizeObserver && (this.resizeObserver.disconnect(), this.resizeObserver = null), (e = this.unsubscribeOnScroll) === null || e === void 0 || e.forEach((t) => t()), this.unsubscribeOnScroll = [];
  }
  createDelay(e = 10) {
    let t, r;
    const i = () => {
      t && (clearTimeout(t), t = void 0), r && (r(), r = void 0);
    };
    return this.timeouts.push(i), () => new Promise((o, s) => {
      i(), r = s, t = setTimeout(() => {
        t = void 0, r = void 0, o();
      }, e);
    });
  }
  getHeight(e, t) {
    var r;
    const i = ((r = this.audioData) === null || r === void 0 ? void 0 : r.numberOfChannels) || 1;
    return hl({
      optionsHeight: e,
      optionsSplitChannels: t,
      parentHeight: this.parent.clientHeight,
      numberOfChannels: i,
      defaultHeight: ei
    });
  }
  convertColorValues(e) {
    return ml(e, this.getPixelRatio());
  }
  getPixelRatio() {
    return pl(window.devicePixelRatio);
  }
  renderBarWaveform(e, t, r, i) {
    const {
      width: o,
      height: s
    } = r.canvas, {
      halfHeight: a,
      barWidth: c,
      barRadius: l,
      barIndexScale: u,
      barSpacing: d
    } = cl({
      width: o,
      height: s,
      length: (e[0] || []).length,
      options: t,
      pixelRatio: this.getPixelRatio()
    }), h = fl({
      channelData: e,
      barIndexScale: u,
      barSpacing: d,
      barWidth: c,
      halfHeight: a,
      vScale: i,
      canvasHeight: s,
      barAlign: t.barAlign
    });
    r.beginPath();
    for (const p of h)
      l && "roundRect" in r ? r.roundRect(p.x, p.y, p.width, p.height, l) : r.rect(p.x, p.y, p.width, p.height);
    r.fill(), r.closePath();
  }
  renderLineWaveform(e, t, r, i) {
    const {
      width: o,
      height: s
    } = r.canvas, a = Sl({
      channelData: e,
      width: o,
      height: s,
      vScale: i
    });
    r.beginPath();
    for (const c of a)
      if (c.length) {
        r.moveTo(c[0].x, c[0].y);
        for (let l = 1; l < c.length; l++) {
          const u = c[l];
          r.lineTo(u.x, u.y);
        }
      }
    r.fill(), r.closePath();
  }
  renderWaveform(e, t, r) {
    if (r.fillStyle = this.convertColorValues(t.waveColor), t.renderFunction) {
      t.renderFunction(e, r);
      return;
    }
    const i = wl({
      channelData: e,
      barHeight: t.barHeight,
      normalize: t.normalize
    });
    if (ti(t)) {
      this.renderBarWaveform(e, t, r, i);
      return;
    }
    this.renderLineWaveform(e, t, r, i);
  }
  renderSingleCanvas(e, t, r, i, o, s, a) {
    const c = this.getPixelRatio(), l = document.createElement("canvas");
    l.width = Math.round(r * c), l.height = Math.round(i * c), l.style.width = `${r}px`, l.style.height = `${i}px`, l.style.left = `${Math.round(o)}px`, s.appendChild(l);
    const u = l.getContext("2d");
    if (t.renderFunction ? (u.fillStyle = this.convertColorValues(t.waveColor), t.renderFunction(e, u)) : this.renderWaveform(e, t, u), l.width > 0 && l.height > 0) {
      const d = l.cloneNode(), h = d.getContext("2d");
      h.drawImage(l, 0, 0), h.globalCompositeOperation = "source-in", h.fillStyle = this.convertColorValues(t.progressColor), h.fillRect(0, 0, l.width, l.height), a.appendChild(d);
    }
  }
  renderMultiCanvas(e, t, r, i, o, s) {
    const a = this.getPixelRatio(), {
      clientWidth: c
    } = this.scrollContainer, l = r / a, u = vl({
      clientWidth: c,
      totalWidth: l,
      options: t
    });
    let d = {};
    if (u === 0) return;
    const h = (m) => {
      if (m < 0 || m >= v || d[m]) return;
      d[m] = !0;
      const b = m * u;
      let w = Math.min(l - b, u);
      if (w = ni(w, t), w <= 0) return;
      const C = bl({
        channelData: e,
        offset: b,
        clampedWidth: w,
        totalWidth: l
      });
      this.renderSingleCanvas(C, t, w, i, b, o, s);
    }, p = () => {
      yl(Object.keys(d).length) && (o.innerHTML = "", s.innerHTML = "", d = {});
    }, v = Math.ceil(l / u);
    if (!this.isScrollable) {
      for (let m = 0; m < v; m++)
        h(m);
      return;
    }
    if (ar({
      scrollLeft: this.scrollContainer.scrollLeft,
      totalWidth: l,
      numCanvases: v
    }).forEach((m) => h(m)), v > 1) {
      const m = this.on("scroll", () => {
        const {
          scrollLeft: b
        } = this.scrollContainer;
        p(), ar({
          scrollLeft: b,
          totalWidth: l,
          numCanvases: v
        }).forEach((w) => h(w));
      });
      this.unsubscribeOnScroll.push(m);
    }
  }
  renderChannel(e, t, r, i) {
    var {
      overlay: o
    } = t, s = Cl(t, ["overlay"]);
    const a = document.createElement("div"), c = this.getHeight(s.height, s.splitChannels);
    a.style.height = `${c}px`, o && i > 0 && (a.style.marginTop = `-${c}px`), this.canvasWrapper.style.minHeight = `${c}px`, this.canvasWrapper.appendChild(a);
    const l = a.cloneNode();
    this.progressWrapper.appendChild(l), this.renderMultiCanvas(e, s, r, c, a, l);
  }
  render(e) {
    return cr(this, void 0, void 0, function* () {
      var t;
      this.timeouts.forEach((l) => l()), this.timeouts = [], this.canvasWrapper.innerHTML = "", this.progressWrapper.innerHTML = "", this.options.width != null && (this.scrollContainer.style.width = typeof this.options.width == "number" ? `${this.options.width}px` : this.options.width);
      const r = this.getPixelRatio(), i = this.scrollContainer.clientWidth, {
        scrollWidth: o,
        isScrollable: s,
        useParentWidth: a,
        width: c
      } = gl({
        duration: e.duration,
        minPxPerSec: this.options.minPxPerSec || 0,
        parentWidth: i,
        fillParent: this.options.fillParent,
        pixelRatio: r
      });
      if (this.isScrollable = s, this.wrapper.style.width = a ? "100%" : `${o}px`, this.scrollContainer.style.overflowX = this.isScrollable ? "auto" : "hidden", this.scrollContainer.classList.toggle("noScrollbar", !!this.options.hideScrollbar), this.cursor.style.backgroundColor = `${this.options.cursorColor || this.options.progressColor}`, this.cursor.style.width = `${this.options.cursorWidth}px`, this.audioData = e, this.emit("render"), this.options.splitChannels)
        for (let l = 0; l < e.numberOfChannels; l++) {
          const u = Object.assign(Object.assign({}, this.options), (t = this.options.splitChannels) === null || t === void 0 ? void 0 : t[l]);
          this.renderChannel([e.getChannelData(l)], u, c, l);
        }
      else {
        const l = [e.getChannelData(0)];
        e.numberOfChannels > 1 && l.push(e.getChannelData(1)), this.renderChannel(l, this.options, c, 0);
      }
      Promise.resolve().then(() => this.emit("rendered"));
    });
  }
  reRender() {
    if (this.unsubscribeOnScroll.forEach((r) => r()), this.unsubscribeOnScroll = [], !this.audioData) return;
    const {
      scrollWidth: e
    } = this.scrollContainer, {
      right: t
    } = this.progressWrapper.getBoundingClientRect();
    if (this.render(this.audioData), this.isScrollable && e !== this.scrollContainer.scrollWidth) {
      const {
        right: r
      } = this.progressWrapper.getBoundingClientRect(), i = xl(r - t);
      this.scrollContainer.scrollLeft += i;
    }
  }
  zoom(e) {
    this.options.minPxPerSec = e, this.reRender();
  }
  scrollIntoView(e, t = !1) {
    const {
      scrollLeft: r,
      scrollWidth: i,
      clientWidth: o
    } = this.scrollContainer, s = e * i, a = r, c = r + o, l = o / 2;
    if (this.isDragging)
      s + 30 > c ? this.scrollContainer.scrollLeft += 30 : s - 30 < a && (this.scrollContainer.scrollLeft -= 30);
    else {
      (s < a || s > c) && (this.scrollContainer.scrollLeft = s - (this.options.autoCenter ? l : 0));
      const u = s - r - l;
      t && this.options.autoCenter && u > 0 && (this.scrollContainer.scrollLeft += u);
    }
    {
      const u = this.scrollContainer.scrollLeft, {
        startX: d,
        endX: h
      } = lr({
        scrollLeft: u,
        scrollWidth: i,
        clientWidth: o
      });
      this.emit("scroll", d, h, u, u + o);
    }
  }
  renderProgress(e, t) {
    if (isNaN(e)) return;
    const r = e * 100;
    this.canvasWrapper.style.clipPath = `polygon(${r}% 0%, 100% 0%, 100% 100%, ${r}% 100%)`, this.progressWrapper.style.width = `${r}%`, this.cursor.style.left = `${r}%`, this.cursor.style.transform = this.options.cursorWidth ? `translateX(-${e * this.options.cursorWidth}px)` : "", this.isScrollable && this.options.autoScroll && this.scrollIntoView(e, t);
  }
  exportImage(e, t, r) {
    return cr(this, void 0, void 0, function* () {
      const i = this.canvasWrapper.querySelectorAll("canvas");
      if (!i.length)
        throw new Error("No waveform data");
      if (r === "dataURL") {
        const o = Array.from(i).map((s) => s.toDataURL(e, t));
        return Promise.resolve(o);
      }
      return Promise.all(Array.from(i).map((o) => new Promise((s, a) => {
        o.toBlob((c) => {
          c ? s(c) : a(new Error("Could not export image"));
        }, e, t);
      })));
    });
  }
}
class _l extends Ge {
  constructor() {
    super(...arguments), this.animationFrameId = null, this.isRunning = !1;
  }
  start() {
    if (this.isRunning) return;
    this.isRunning = !0;
    const e = () => {
      this.isRunning && (this.emit("tick"), this.animationFrameId = requestAnimationFrame(e));
    };
    e();
  }
  stop() {
    this.isRunning = !1, this.animationFrameId !== null && (cancelAnimationFrame(this.animationFrameId), this.animationFrameId = null);
  }
  destroy() {
    this.stop();
  }
}
var Xt = function(n, e, t, r) {
  function i(o) {
    return o instanceof t ? o : new t(function(s) {
      s(o);
    });
  }
  return new (t || (t = Promise))(function(o, s) {
    function a(u) {
      try {
        l(r.next(u));
      } catch (d) {
        s(d);
      }
    }
    function c(u) {
      try {
        l(r.throw(u));
      } catch (d) {
        s(d);
      }
    }
    function l(u) {
      u.done ? o(u.value) : i(u.value).then(a, c);
    }
    l((r = r.apply(n, e || [])).next());
  });
};
class Gt extends Ge {
  constructor(e = new AudioContext()) {
    super(), this.bufferNode = null, this.playStartTime = 0, this.playedDuration = 0, this._muted = !1, this._playbackRate = 1, this._duration = void 0, this.buffer = null, this.currentSrc = "", this.paused = !0, this.crossOrigin = null, this.seeking = !1, this.autoplay = !1, this.addEventListener = this.on, this.removeEventListener = this.un, this.audioContext = e, this.gainNode = this.audioContext.createGain(), this.gainNode.connect(this.audioContext.destination);
  }
  load() {
    return Xt(this, void 0, void 0, function* () {
    });
  }
  get src() {
    return this.currentSrc;
  }
  set src(e) {
    if (this.currentSrc = e, this._duration = void 0, !e) {
      this.buffer = null, this.emit("emptied");
      return;
    }
    fetch(e).then((t) => {
      if (t.status >= 400)
        throw new Error(`Failed to fetch ${e}: ${t.status} (${t.statusText})`);
      return t.arrayBuffer();
    }).then((t) => this.currentSrc !== e ? null : this.audioContext.decodeAudioData(t)).then((t) => {
      this.currentSrc === e && (this.buffer = t, this.emit("loadedmetadata"), this.emit("canplay"), this.autoplay && this.play());
    }).catch((t) => {
      console.error("WebAudioPlayer load error:", t);
    });
  }
  _play() {
    if (!this.paused) return;
    this.paused = !1, this.bufferNode && (this.bufferNode.onended = null, this.bufferNode.disconnect()), this.bufferNode = this.audioContext.createBufferSource(), this.buffer && (this.bufferNode.buffer = this.buffer), this.bufferNode.playbackRate.value = this._playbackRate, this.bufferNode.connect(this.gainNode);
    let e = this.playedDuration * this._playbackRate;
    (e >= this.duration || e < 0) && (e = 0, this.playedDuration = 0), this.bufferNode.start(this.audioContext.currentTime, e), this.playStartTime = this.audioContext.currentTime, this.bufferNode.onended = () => {
      this.currentTime >= this.duration && (this.pause(), this.emit("ended"));
    };
  }
  _pause() {
    var e;
    this.paused = !0, (e = this.bufferNode) === null || e === void 0 || e.stop(), this.playedDuration += this.audioContext.currentTime - this.playStartTime;
  }
  play() {
    return Xt(this, void 0, void 0, function* () {
      this.paused && (this._play(), this.emit("play"));
    });
  }
  pause() {
    this.paused || (this._pause(), this.emit("pause"));
  }
  stopAt(e) {
    const t = e - this.currentTime, r = this.bufferNode;
    r == null || r.stop(this.audioContext.currentTime + t), r == null || r.addEventListener("ended", () => {
      r === this.bufferNode && (this.bufferNode = null, this.pause());
    }, {
      once: !0
    });
  }
  setSinkId(e) {
    return Xt(this, void 0, void 0, function* () {
      return this.audioContext.setSinkId(e);
    });
  }
  get playbackRate() {
    return this._playbackRate;
  }
  set playbackRate(e) {
    this._playbackRate = e, this.bufferNode && (this.bufferNode.playbackRate.value = e);
  }
  get currentTime() {
    return (this.paused ? this.playedDuration : this.playedDuration + (this.audioContext.currentTime - this.playStartTime)) * this._playbackRate;
  }
  set currentTime(e) {
    const t = !this.paused;
    t && this._pause(), this.playedDuration = e / this._playbackRate, t && this._play(), this.emit("seeking"), this.emit("timeupdate");
  }
  get duration() {
    var e, t;
    return (e = this._duration) !== null && e !== void 0 ? e : ((t = this.buffer) === null || t === void 0 ? void 0 : t.duration) || 0;
  }
  set duration(e) {
    this._duration = e;
  }
  get volume() {
    return this.gainNode.gain.value;
  }
  set volume(e) {
    this.gainNode.gain.value = e, this.emit("volumechange");
  }
  get muted() {
    return this._muted;
  }
  set muted(e) {
    this._muted !== e && (this._muted = e, this._muted ? this.gainNode.disconnect() : this.gainNode.connect(this.audioContext.destination));
  }
  canPlayType(e) {
    return /^(audio|video)\//.test(e);
  }
  /** Get the GainNode used to play the audio. Can be used to attach filters. */
  getGainNode() {
    return this.gainNode;
  }
  /** Get decoded audio */
  getChannelData() {
    const e = [];
    if (!this.buffer) return e;
    const t = this.buffer.numberOfChannels;
    for (let r = 0; r < t; r++)
      e.push(this.buffer.getChannelData(r));
    return e;
  }
  /**
   * Imitate `HTMLElement.removeAttribute` for compatibility with `Player`.
   */
  removeAttribute(e) {
    switch (e) {
      case "src":
        this.src = "";
        break;
      case "playbackRate":
        this.playbackRate = 0;
        break;
      case "currentTime":
        this.currentTime = 0;
        break;
      case "duration":
        this.duration = 0;
        break;
      case "volume":
        this.volume = 0;
        break;
      case "muted":
        this.muted = !1;
        break;
    }
  }
}
var Le = function(n, e, t, r) {
  function i(o) {
    return o instanceof t ? o : new t(function(s) {
      s(o);
    });
  }
  return new (t || (t = Promise))(function(o, s) {
    function a(u) {
      try {
        l(r.next(u));
      } catch (d) {
        s(d);
      }
    }
    function c(u) {
      try {
        l(r.throw(u));
      } catch (d) {
        s(d);
      }
    }
    function l(u) {
      u.done ? o(u.value) : i(u.value).then(a, c);
    }
    l((r = r.apply(n, e || [])).next());
  });
};
const Rl = {
  waveColor: "#999",
  progressColor: "#555",
  cursorWidth: 1,
  minPxPerSec: 0,
  fillParent: !0,
  interact: !0,
  dragToSeek: !1,
  autoScroll: !0,
  autoCenter: !0,
  sampleRate: 8e3
};
class qe extends ol {
  /** Create a new WaveSurfer instance */
  static create(e) {
    return new qe(e);
  }
  /** Create a new WaveSurfer instance */
  constructor(e) {
    const t = e.media || (e.backend === "WebAudio" ? new Gt() : void 0);
    super({
      media: t,
      mediaControls: e.mediaControls,
      autoplay: e.autoplay,
      playbackRate: e.audioRate
    }), this.plugins = [], this.decodedData = null, this.stopAtPosition = null, this.subscriptions = [], this.mediaSubscriptions = [], this.abortController = null, this.options = Object.assign({}, Rl, e), this.timer = new _l();
    const r = t ? void 0 : this.getMediaElement();
    this.renderer = new El(this.options, r), this.initPlayerEvents(), this.initRendererEvents(), this.initTimerEvents(), this.initPlugins();
    const i = this.options.url || this.getSrc() || "";
    Promise.resolve().then(() => {
      this.emit("init");
      const {
        peaks: o,
        duration: s
      } = this.options;
      (i || o && s) && this.load(i, o, s).catch((a) => {
        this.emit("error", a instanceof Error ? a : new Error(String(a)));
      });
    });
  }
  updateProgress(e = this.getCurrentTime()) {
    return this.renderer.renderProgress(e / this.getDuration(), this.isPlaying()), e;
  }
  initTimerEvents() {
    this.subscriptions.push(this.timer.on("tick", () => {
      if (!this.isSeeking()) {
        const e = this.updateProgress();
        this.emit("timeupdate", e), this.emit("audioprocess", e), this.stopAtPosition != null && this.isPlaying() && e >= this.stopAtPosition && this.pause();
      }
    }));
  }
  initPlayerEvents() {
    this.isPlaying() && (this.emit("play"), this.timer.start()), this.mediaSubscriptions.push(this.onMediaEvent("timeupdate", () => {
      const e = this.updateProgress();
      this.emit("timeupdate", e);
    }), this.onMediaEvent("play", () => {
      this.emit("play"), this.timer.start();
    }), this.onMediaEvent("pause", () => {
      this.emit("pause"), this.timer.stop(), this.stopAtPosition = null;
    }), this.onMediaEvent("emptied", () => {
      this.timer.stop(), this.stopAtPosition = null;
    }), this.onMediaEvent("ended", () => {
      this.emit("timeupdate", this.getDuration()), this.emit("finish"), this.stopAtPosition = null;
    }), this.onMediaEvent("seeking", () => {
      this.emit("seeking", this.getCurrentTime());
    }), this.onMediaEvent("error", () => {
      var e;
      this.emit("error", (e = this.getMediaElement().error) !== null && e !== void 0 ? e : new Error("Media error")), this.stopAtPosition = null;
    }));
  }
  initRendererEvents() {
    this.subscriptions.push(
      // Seek on click
      this.renderer.on("click", (e, t) => {
        this.options.interact && (this.seekTo(e), this.emit("interaction", e * this.getDuration()), this.emit("click", e, t));
      }),
      // Double click
      this.renderer.on("dblclick", (e, t) => {
        this.emit("dblclick", e, t);
      }),
      // Scroll
      this.renderer.on("scroll", (e, t, r, i) => {
        const o = this.getDuration();
        this.emit("scroll", e * o, t * o, r, i);
      }),
      // Redraw
      this.renderer.on("render", () => {
        this.emit("redraw");
      }),
      // RedrawComplete
      this.renderer.on("rendered", () => {
        this.emit("redrawcomplete");
      }),
      // DragStart
      this.renderer.on("dragstart", (e) => {
        this.emit("dragstart", e);
      }),
      // DragEnd
      this.renderer.on("dragend", (e) => {
        this.emit("dragend", e);
      }),
      // Resize
      this.renderer.on("resize", () => {
        this.emit("resize");
      })
    );
    {
      let e;
      const t = this.renderer.on("drag", (r) => {
        var i;
        if (!this.options.interact) return;
        this.renderer.renderProgress(r), clearTimeout(e);
        let o = 0;
        const s = this.options.dragToSeek;
        this.isPlaying() ? o = 0 : s === !0 ? o = 200 : s && typeof s == "object" && (o = (i = s.debounceTime) !== null && i !== void 0 ? i : 200), e = setTimeout(() => {
          this.seekTo(r);
        }, o), this.emit("interaction", r * this.getDuration()), this.emit("drag", r);
      });
      this.subscriptions.push(() => {
        clearTimeout(e), t();
      });
    }
  }
  initPlugins() {
    var e;
    !((e = this.options.plugins) === null || e === void 0) && e.length && this.options.plugins.forEach((t) => {
      this.registerPlugin(t);
    });
  }
  unsubscribePlayerEvents() {
    this.mediaSubscriptions.forEach((e) => e()), this.mediaSubscriptions = [];
  }
  /** Set new wavesurfer options and re-render it */
  setOptions(e) {
    this.options = Object.assign({}, this.options, e), e.duration && !e.peaks && (this.decodedData = rt.createBuffer(this.exportPeaks(), e.duration)), e.peaks && e.duration && (this.decodedData = rt.createBuffer(e.peaks, e.duration)), this.renderer.setOptions(this.options), e.audioRate && this.setPlaybackRate(e.audioRate), e.mediaControls != null && (this.getMediaElement().controls = e.mediaControls);
  }
  /** Register a wavesurfer.js plugin */
  registerPlugin(e) {
    if (this.plugins.includes(e))
      return e;
    e._init(this), this.plugins.push(e);
    const t = e.once("destroy", () => {
      this.plugins = this.plugins.filter((r) => r !== e), this.subscriptions = this.subscriptions.filter((r) => r !== t);
    });
    return this.subscriptions.push(t), e;
  }
  /** Unregister a wavesurfer.js plugin */
  unregisterPlugin(e) {
    this.plugins = this.plugins.filter((t) => t !== e), e.destroy();
  }
  /** For plugins only: get the waveform wrapper div */
  getWrapper() {
    return this.renderer.getWrapper();
  }
  /** For plugins only: get the scroll container client width */
  getWidth() {
    return this.renderer.getWidth();
  }
  /** Get the current scroll position in pixels */
  getScroll() {
    return this.renderer.getScroll();
  }
  /** Set the current scroll position in pixels */
  setScroll(e) {
    return this.renderer.setScroll(e);
  }
  /** Move the start of the viewing window to a specific time in the audio (in seconds) */
  setScrollTime(e) {
    const t = e / this.getDuration();
    this.renderer.setScrollPercentage(t);
  }
  /** Get all registered plugins */
  getActivePlugins() {
    return this.plugins;
  }
  loadAudio(e, t, r, i) {
    return Le(this, void 0, void 0, function* () {
      var o;
      if (this.emit("load", e), !this.options.media && this.isPlaying() && this.pause(), this.decodedData = null, this.stopAtPosition = null, (o = this.abortController) === null || o === void 0 || o.abort(), this.abortController = null, !t && !r) {
        const a = this.options.fetchParams || {};
        window.AbortController && !a.signal && (this.abortController = new AbortController(), a.signal = this.abortController.signal);
        const c = (u) => this.emit("loading", u);
        t = yield rl.fetchBlob(e, c, a);
        const l = this.options.blobMimeType;
        l && (t = new Blob([t], {
          type: l
        }));
      }
      this.setSrc(e, t);
      const s = yield new Promise((a) => {
        const c = i || this.getDuration();
        c ? a(c) : this.mediaSubscriptions.push(this.onMediaEvent("loadedmetadata", () => a(this.getDuration()), {
          once: !0
        }));
      });
      if (!e && !t) {
        const a = this.getMediaElement();
        a instanceof Gt && (a.duration = s);
      }
      if (r)
        this.decodedData = rt.createBuffer(r, s || 0);
      else if (t) {
        const a = yield t.arrayBuffer();
        this.decodedData = yield rt.decode(a, this.options.sampleRate);
      }
      this.decodedData && (this.emit("decode", this.getDuration()), this.renderer.render(this.decodedData)), this.emit("ready", this.getDuration());
    });
  }
  /** Load an audio file by URL, with optional pre-decoded audio data */
  load(e, t, r) {
    return Le(this, void 0, void 0, function* () {
      try {
        return yield this.loadAudio(e, void 0, t, r);
      } catch (i) {
        throw this.emit("error", i), i;
      }
    });
  }
  /** Load an audio blob */
  loadBlob(e, t, r) {
    return Le(this, void 0, void 0, function* () {
      try {
        return yield this.loadAudio("", e, t, r);
      } catch (i) {
        throw this.emit("error", i), i;
      }
    });
  }
  /** Zoom the waveform by a given pixels-per-second factor */
  zoom(e) {
    if (!this.decodedData)
      throw new Error("No audio loaded");
    this.renderer.zoom(e), this.emit("zoom", e);
  }
  /** Get the decoded audio data */
  getDecodedData() {
    return this.decodedData;
  }
  /** Get decoded peaks */
  exportPeaks({
    channels: e = 2,
    maxLength: t = 8e3,
    precision: r = 1e4
  } = {}) {
    if (!this.decodedData)
      throw new Error("The audio has not been decoded yet");
    const i = Math.min(e, this.decodedData.numberOfChannels), o = [];
    for (let s = 0; s < i; s++) {
      const a = this.decodedData.getChannelData(s), c = [], l = a.length / t;
      for (let u = 0; u < t; u++) {
        const d = a.slice(Math.floor(u * l), Math.ceil((u + 1) * l));
        let h = 0;
        for (let p = 0; p < d.length; p++) {
          const v = d[p];
          Math.abs(v) > Math.abs(h) && (h = v);
        }
        c.push(Math.round(h * r) / r);
      }
      o.push(c);
    }
    return o;
  }
  /** Get the duration of the audio in seconds */
  getDuration() {
    let e = super.getDuration() || 0;
    return (e === 0 || e === 1 / 0) && this.decodedData && (e = this.decodedData.duration), e;
  }
  /** Toggle if the waveform should react to clicks */
  toggleInteraction(e) {
    this.options.interact = e;
  }
  /** Jump to a specific time in the audio (in seconds) */
  setTime(e) {
    this.stopAtPosition = null, super.setTime(e), this.updateProgress(e), this.emit("timeupdate", e);
  }
  /** Seek to a ratio of audio as [0..1] (0 = beginning, 1 = end) */
  seekTo(e) {
    const t = this.getDuration() * e;
    this.setTime(t);
  }
  /** Start playing the audio */
  play(e, t) {
    const r = Object.create(null, {
      play: {
        get: () => super.play
      }
    });
    return Le(this, void 0, void 0, function* () {
      e != null && this.setTime(e);
      const i = yield r.play.call(this);
      return t != null && (this.media instanceof Gt ? this.media.stopAt(t) : this.stopAtPosition = t), i;
    });
  }
  /** Play or pause the audio */
  playPause() {
    return Le(this, void 0, void 0, function* () {
      return this.isPlaying() ? this.pause() : this.play();
    });
  }
  /** Stop the audio and go to the beginning */
  stop() {
    this.pause(), this.setTime(0);
  }
  /** Skip N or -N seconds from the current position */
  skip(e) {
    this.setTime(this.getCurrentTime() + e);
  }
  /** Empty the waveform */
  empty() {
    this.load("", [[0]], 1e-3);
  }
  /** Set HTML media element */
  setMediaElement(e) {
    this.unsubscribePlayerEvents(), super.setMediaElement(e), this.initPlayerEvents();
  }
  exportImage() {
    return Le(this, arguments, void 0, function* (e = "image/png", t = 1, r = "dataURL") {
      return this.renderer.exportImage(e, t, r);
    });
  }
  /** Unmount wavesurfer */
  destroy() {
    var e;
    this.emit("destroy"), (e = this.abortController) === null || e === void 0 || e.abort(), this.plugins.forEach((t) => t.destroy()), this.subscriptions.forEach((t) => t()), this.unsubscribePlayerEvents(), this.timer.destroy(), this.renderer.destroy(), super.destroy();
  }
}
qe.BasePlugin = Ka;
qe.dom = el;
function Pl({
  container: n,
  onStop: e
}) {
  const t = he(null), [r, i] = $e(!1), o = ct(() => {
    var c;
    (c = t.current) == null || c.startRecording();
  }), s = ct(() => {
    var c;
    (c = t.current) == null || c.stopRecording();
  }), a = ct(e);
  return Ce(() => {
    if (n) {
      const l = qe.create({
        normalize: !1,
        container: n
      }).registerPlugin(pn.create());
      t.current = l, l.on("record-start", () => {
        i(!0);
      }), l.on("record-end", (u) => {
        a(u), i(!1);
      });
    }
  }, [n, a]), {
    recording: r,
    start: o,
    stop: s
  };
}
function Tl(n) {
  const e = function(a, c, l) {
    for (let u = 0; u < l.length; u++)
      a.setUint8(c + u, l.charCodeAt(u));
  }, t = n.numberOfChannels, r = n.length * t * 2 + 44, i = new ArrayBuffer(r), o = new DataView(i);
  let s = 0;
  e(o, s, "RIFF"), s += 4, o.setUint32(s, r - 8, !0), s += 4, e(o, s, "WAVE"), s += 4, e(o, s, "fmt "), s += 4, o.setUint32(s, 16, !0), s += 4, o.setUint16(s, 1, !0), s += 2, o.setUint16(s, t, !0), s += 2, o.setUint32(s, n.sampleRate, !0), s += 4, o.setUint32(s, n.sampleRate * 2 * t, !0), s += 4, o.setUint16(s, t * 2, !0), s += 2, o.setUint16(s, 16, !0), s += 2, e(o, s, "data"), s += 4, o.setUint32(s, n.length * t * 2, !0), s += 4;
  for (let a = 0; a < n.numberOfChannels; a++) {
    const c = n.getChannelData(a);
    for (let l = 0; l < c.length; l++)
      o.setInt16(s, c[l] * 65535, !0), s += 2;
  }
  return new Uint8Array(i);
}
async function Ml(n, e, t) {
  const r = await n.arrayBuffer(), o = await new AudioContext().decodeAudioData(r), s = new AudioContext(), a = o.numberOfChannels, c = o.sampleRate;
  let l = o.length, u = 0;
  const d = s.createBuffer(a, l, c);
  for (let h = 0; h < a; h++) {
    const p = o.getChannelData(h), v = d.getChannelData(h);
    for (let g = 0; g < l; g++)
      v[g] = p[u + g];
  }
  return Tl(d);
}
const Ll = (n) => !!n.name, ze = (n) => {
  var e;
  return {
    text: (n == null ? void 0 : n.text) || "",
    files: ((e = n == null ? void 0 : n.files) == null ? void 0 : e.map((t) => t.path)) || []
  };
}, Il = Ao(({
  onValueChange: n,
  onChange: e,
  onPasteFile: t,
  onUpload: r,
  onSubmit: i,
  onRemove: o,
  onDownload: s,
  onDrop: a,
  onPreview: c,
  upload: l,
  onCancel: u,
  children: d,
  readOnly: h,
  loading: p,
  disabled: v,
  placeholder: g,
  elRef: m,
  slots: b,
  mode: w,
  // setSlotParams,
  uploadConfig: C,
  value: E,
  ...S
}) => {
  const [x, T] = $e(!1), R = bi(), O = he(null), [P, M] = $e(!1), $ = ir(S.actions, !0), N = ir(S.footer, !0), {
    start: W,
    stop: A,
    recording: U
  } = Pl({
    container: O.current,
    async onStop(B) {
      const L = new File([await Ml(B)], `${Date.now()}_recording_result.wav`, {
        type: "audio/wav"
      });
      ee(L);
    }
  }), [F, I] = Ua({
    onValueChange: n,
    value: E
  }), y = qt(() => mi(C), [C]), le = v || (y == null ? void 0 : y.disabled) || p || h || P, ee = ct(async (B) => {
    try {
      if (le)
        return;
      M(!0);
      const L = y == null ? void 0 : y.maxCount;
      if (typeof L == "number" && L > 0 && J.length >= L)
        return;
      let j = Array.isArray(B) ? B : [B];
      if (L === 1)
        j = j.slice(0, 1);
      else if (j.length === 0) {
        M(!1);
        return;
      } else if (typeof L == "number") {
        const X = L - J.length;
        j = j.slice(0, X < 0 ? 0 : X);
      }
      const ne = J, Y = j.map((X) => ({
        ...X,
        size: X.size,
        uid: `${X.name}-${Date.now()}`,
        name: X.name,
        status: "uploading"
      }));
      V((X) => [...L === 1 ? [] : X, ...Y]);
      const re = (await l(j)).filter(Boolean).map((X, me) => ({
        ...X,
        uid: Y[me].uid
      })), pe = L === 1 ? re : [...ne, ...re];
      r == null || r(re.map((X) => X.path)), M(!1);
      const se = {
        ...F,
        files: pe
      };
      return e == null || e(ze(se)), I(se), re;
    } catch {
      return M(!1), [];
    }
  }), [J, V] = $e(() => (F == null ? void 0 : F.files) || []);
  Ce(() => {
    V((F == null ? void 0 : F.files) || []);
  }, [F == null ? void 0 : F.files]);
  const z = qt(() => {
    const B = {};
    return J.map((L) => {
      if (!Ll(L)) {
        const j = L.uid || L.url || L.path;
        return B[j] || (B[j] = 0), B[j]++, {
          ...L,
          name: L.orig_name || L.path,
          uid: L.uid || j + "-" + B[j],
          status: "done"
        };
      }
      return L;
    }) || [];
  }, [J]), Q = (y == null ? void 0 : y.allowUpload) ?? !0, te = Q ? y == null ? void 0 : y.allowSpeech : !1, ce = Q ? y == null ? void 0 : y.allowPasteFile : !1, Se = /* @__PURE__ */ q.jsx(Bi, {
    title: y == null ? void 0 : y.uploadButtonTooltip,
    children: /* @__PURE__ */ q.jsx(Hi, {
      count: ((y == null ? void 0 : y.showCount) ?? !0) && !x ? z.length : 0,
      children: /* @__PURE__ */ q.jsx(ke, {
        onClick: () => {
          T(!x);
        },
        color: "default",
        variant: "text",
        icon: /* @__PURE__ */ q.jsx(ki, {})
      })
    })
  });
  return /* @__PURE__ */ q.jsxs(q.Fragment, {
    children: [/* @__PURE__ */ q.jsx("div", {
      style: {
        display: "none"
      },
      ref: O
    }), /* @__PURE__ */ q.jsx("div", {
      style: {
        display: "none"
      },
      children: d
    }), /* @__PURE__ */ q.jsx(ln, {
      ...S,
      value: F == null ? void 0 : F.text,
      ref: m,
      disabled: v,
      readOnly: h,
      allowSpeech: te ? {
        recording: U,
        onRecordingChange(B) {
          le || (B ? W() : A());
        }
      } : !1,
      placeholder: g,
      loading: p,
      onSubmit: () => {
        R || i == null || i(ze(F));
      },
      onCancel: () => {
        u == null || u();
      },
      onChange: (B) => {
        const L = {
          ...F,
          text: B
        };
        e == null || e(ze(L)), I(L);
      },
      onPasteFile: async (B, L) => {
        if (!(ce ?? !0))
          return;
        const j = await ee(Array.from(L));
        j && (t == null || t(j.map((ne) => ne.path)));
      },
      prefix: /* @__PURE__ */ q.jsxs(q.Fragment, {
        children: [Q && w !== "block" ? Se : null, b.prefix ? /* @__PURE__ */ q.jsx(je, {
          slot: b.prefix
        }) : null]
      }),
      actions: w === "block" ? !1 : b.actions ? /* @__PURE__ */ q.jsx(je, {
        slot: b.actions
      }) : $ || S.actions,
      footer: w === "block" ? ({
        components: B
      }) => {
        const {
          SendButton: L,
          SpeechButton: j,
          LoadingButton: ne
        } = B;
        return /* @__PURE__ */ q.jsxs(ft, {
          align: "center",
          justify: "space-between",
          gap: "small",
          className: "ms-gr-pro-multimodal-input-footer",
          children: [/* @__PURE__ */ q.jsxs("div", {
            className: "ms-gr-pro-multimodal-input-footer-extra",
            children: [Q ? Se : null, b.footer ? /* @__PURE__ */ q.jsx(je, {
              slot: b.footer
            }) : null]
          }), /* @__PURE__ */ q.jsxs(ft, {
            gap: "small",
            className: "ms-gr-pro-multimodal-input-footer-actions",
            children: [te ? /* @__PURE__ */ q.jsx(j, {}) : null, p ? /* @__PURE__ */ q.jsx(ne, {}) : /* @__PURE__ */ q.jsx(L, {})]
          })]
        });
      } : b.footer ? /* @__PURE__ */ q.jsx(je, {
        slot: b.footer
      }) : N || S.footer,
      header: Q ? /* @__PURE__ */ q.jsx(ln.Header, {
        title: (y == null ? void 0 : y.title) || "Attachments",
        open: x,
        onOpenChange: T,
        children: /* @__PURE__ */ q.jsx(Xr, {
          ...Va(gi(y, ["title", "placeholder", "showCount", "buttonTooltip", "allowPasteFile"])),
          imageProps: {
            ...y == null ? void 0 : y.imageProps
          },
          disabled: le,
          getDropContainer: () => y != null && y.fullscreenDrop ? document.body : null,
          items: z,
          placeholder: (B) => {
            var j, ne, Y, re, pe, se, X, me, ye, G, ie, oe;
            const L = B === "drop";
            return {
              title: L ? ((ne = (j = y == null ? void 0 : y.placeholder) == null ? void 0 : j.drop) == null ? void 0 : ne.title) ?? "Drop file here" : ((re = (Y = y == null ? void 0 : y.placeholder) == null ? void 0 : Y.inline) == null ? void 0 : re.title) ?? "Upload files",
              description: L ? ((se = (pe = y == null ? void 0 : y.placeholder) == null ? void 0 : pe.drop) == null ? void 0 : se.description) ?? void 0 : ((me = (X = y == null ? void 0 : y.placeholder) == null ? void 0 : X.inline) == null ? void 0 : me.description) ?? "Click or drag files to this area to upload",
              icon: L ? ((G = (ye = y == null ? void 0 : y.placeholder) == null ? void 0 : ye.drop) == null ? void 0 : G.icon) ?? void 0 : ((oe = (ie = y == null ? void 0 : y.placeholder) == null ? void 0 : ie.inline) == null ? void 0 : oe.icon) ?? /* @__PURE__ */ q.jsx(Di, {})
            };
          },
          onDownload: s,
          onPreview: c,
          onDrop: a,
          onChange: async (B) => {
            try {
              const L = B.file, j = B.fileList, ne = z.findIndex((Y) => Y.uid === L.uid);
              if (ne !== -1) {
                if (le)
                  return;
                o == null || o(L);
                const Y = J.slice();
                Y.splice(ne, 1);
                const re = {
                  ...F,
                  files: Y
                };
                I(re), e == null || e(ze(re));
              } else {
                if (le)
                  return;
                M(!0);
                let Y = j.filter((G) => G.status !== "done");
                const re = y == null ? void 0 : y.maxCount;
                if (re === 1)
                  Y = Y.slice(0, 1);
                else if (Y.length === 0) {
                  M(!1);
                  return;
                } else if (typeof re == "number") {
                  const G = re - J.length;
                  Y = Y.slice(0, G < 0 ? 0 : G);
                }
                const pe = J, se = Y.map((G) => ({
                  ...G,
                  size: G.size,
                  uid: G.uid,
                  name: G.name,
                  status: "uploading"
                }));
                V((G) => [...re === 1 ? [] : G, ...se]);
                const X = (await l(Y.map((G) => G.originFileObj))).filter(Boolean).map((G, ie) => ({
                  ...G,
                  uid: se[ie].uid
                })), me = re === 1 ? X : [...pe, ...X];
                r == null || r(X.map((G) => G.path)), M(!1);
                const ye = {
                  ...F,
                  files: me
                };
                V(me), n == null || n(ye), e == null || e(ze(ye));
              }
            } catch (L) {
              M(!1), console.error(L);
            }
          },
          customRequest: eo
        })
      }) : b.header ? /* @__PURE__ */ q.jsx(je, {
        slot: b.header
      }) : S.header
    })]
  });
});
export {
  Il as MultimodalInput,
  Il as default
};
