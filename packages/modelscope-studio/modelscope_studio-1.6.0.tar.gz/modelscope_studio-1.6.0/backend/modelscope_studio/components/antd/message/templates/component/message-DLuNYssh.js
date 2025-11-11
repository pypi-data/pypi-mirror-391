import { i as le, a as F, r as ce, Z as T, g as ae, b as ue } from "./Index-egziqlff.js";
const E = window.ms_globals.React, re = window.ms_globals.React.forwardRef, oe = window.ms_globals.React.useRef, se = window.ms_globals.React.useState, K = window.ms_globals.React.useEffect, ie = window.ms_globals.React.useMemo, A = window.ms_globals.ReactDOM.createPortal, de = window.ms_globals.internalContext.useContextPropsContext, fe = window.ms_globals.antd.message;
var me = /\s/;
function _e(e) {
  for (var t = e.length; t-- && me.test(e.charAt(t)); )
    ;
  return t;
}
var pe = /^\s+/;
function ge(e) {
  return e && e.slice(0, _e(e) + 1).replace(pe, "");
}
var z = NaN, he = /^[-+]0x[0-9a-f]+$/i, we = /^0b[01]+$/i, ye = /^0o[0-7]+$/i, be = parseInt;
function D(e) {
  if (typeof e == "number")
    return e;
  if (le(e))
    return z;
  if (F(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = F(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = ge(e);
  var o = we.test(e);
  return o || ye.test(e) ? be(e.slice(2), o ? 2 : 8) : he.test(e) ? z : +e;
}
var L = function() {
  return ce.Date.now();
}, Ee = "Expected a function", ve = Math.max, xe = Math.min;
function Ce(e, t, o) {
  var i, s, n, r, l, u, m = 0, g = !1, c = !1, h = !0;
  if (typeof e != "function")
    throw new TypeError(Ee);
  t = D(t) || 0, F(o) && (g = !!o.leading, c = "maxWait" in o, n = c ? ve(D(o.maxWait) || 0, t) : n, h = "trailing" in o ? !!o.trailing : h);
  function _(d) {
    var y = i, S = s;
    return i = s = void 0, m = d, r = e.apply(S, y), r;
  }
  function b(d) {
    return m = d, l = setTimeout(p, t), g ? _(d) : r;
  }
  function v(d) {
    var y = d - u, S = d - m, M = t - y;
    return c ? xe(M, n - S) : M;
  }
  function f(d) {
    var y = d - u, S = d - m;
    return u === void 0 || y >= t || y < 0 || c && S >= n;
  }
  function p() {
    var d = L();
    if (f(d))
      return w(d);
    l = setTimeout(p, v(d));
  }
  function w(d) {
    return l = void 0, h && i ? _(d) : (i = s = void 0, r);
  }
  function I() {
    l !== void 0 && clearTimeout(l), m = 0, i = u = s = l = void 0;
  }
  function a() {
    return l === void 0 ? r : w(L());
  }
  function x() {
    var d = L(), y = f(d);
    if (i = arguments, s = this, u = d, y) {
      if (l === void 0)
        return b(u);
      if (c)
        return clearTimeout(l), l = setTimeout(p, t), _(u);
    }
    return l === void 0 && (l = setTimeout(p, t)), r;
  }
  return x.cancel = I, x.flush = a, x;
}
var Q = {
  exports: {}
}, P = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ie = E, Se = Symbol.for("react.element"), Re = Symbol.for("react.fragment"), Te = Object.prototype.hasOwnProperty, Oe = Ie.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, ke = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function V(e, t, o) {
  var i, s = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (i in t) Te.call(t, i) && !ke.hasOwnProperty(i) && (s[i] = t[i]);
  if (e && e.defaultProps) for (i in t = e.defaultProps, t) s[i] === void 0 && (s[i] = t[i]);
  return {
    $$typeof: Se,
    type: e,
    key: n,
    ref: r,
    props: s,
    _owner: Oe.current
  };
}
P.Fragment = Re;
P.jsx = V;
P.jsxs = V;
Q.exports = P;
var R = Q.exports;
const {
  SvelteComponent: Pe,
  assign: U,
  binding_callbacks: H,
  check_outros: Le,
  children: $,
  claim_element: ee,
  claim_space: Ne,
  component_subscribe: B,
  compute_slots: Ae,
  create_slot: Fe,
  detach: C,
  element: te,
  empty: G,
  exclude_internal_props: q,
  get_all_dirty_from_scope: We,
  get_slot_changes: je,
  group_outros: Me,
  init: ze,
  insert_hydration: O,
  safe_not_equal: De,
  set_custom_element_data: ne,
  space: Ue,
  transition_in: k,
  transition_out: W,
  update_slot_base: He
} = window.__gradio__svelte__internal, {
  beforeUpdate: Be,
  getContext: Ge,
  onDestroy: qe,
  setContext: Je
} = window.__gradio__svelte__internal;
function J(e) {
  let t, o;
  const i = (
    /*#slots*/
    e[7].default
  ), s = Fe(
    i,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = te("svelte-slot"), s && s.c(), this.h();
    },
    l(n) {
      t = ee(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = $(t);
      s && s.l(r), r.forEach(C), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      O(n, t, r), s && s.m(t, null), e[9](t), o = !0;
    },
    p(n, r) {
      s && s.p && (!o || r & /*$$scope*/
      64) && He(
        s,
        i,
        n,
        /*$$scope*/
        n[6],
        o ? je(
          i,
          /*$$scope*/
          n[6],
          r,
          null
        ) : We(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (k(s, n), o = !0);
    },
    o(n) {
      W(s, n), o = !1;
    },
    d(n) {
      n && C(t), s && s.d(n), e[9](null);
    }
  };
}
function Xe(e) {
  let t, o, i, s, n = (
    /*$$slots*/
    e[4].default && J(e)
  );
  return {
    c() {
      t = te("react-portal-target"), o = Ue(), n && n.c(), i = G(), this.h();
    },
    l(r) {
      t = ee(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), $(t).forEach(C), o = Ne(r), n && n.l(r), i = G(), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      O(r, t, l), e[8](t), O(r, o, l), n && n.m(r, l), O(r, i, l), s = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && k(n, 1)) : (n = J(r), n.c(), k(n, 1), n.m(i.parentNode, i)) : n && (Me(), W(n, 1, 1, () => {
        n = null;
      }), Le());
    },
    i(r) {
      s || (k(n), s = !0);
    },
    o(r) {
      W(n), s = !1;
    },
    d(r) {
      r && (C(t), C(o), C(i)), e[8](null), n && n.d(r);
    }
  };
}
function X(e) {
  const {
    svelteInit: t,
    ...o
  } = e;
  return o;
}
function Ye(e, t, o) {
  let i, s, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = Ae(n);
  let {
    svelteInit: u
  } = t;
  const m = T(X(t)), g = T();
  B(e, g, (a) => o(0, i = a));
  const c = T();
  B(e, c, (a) => o(1, s = a));
  const h = [], _ = Ge("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: v,
    subSlotIndex: f
  } = ae() || {}, p = u({
    parent: _,
    props: m,
    target: g,
    slot: c,
    slotKey: b,
    slotIndex: v,
    subSlotIndex: f,
    onDestroy(a) {
      h.push(a);
    }
  });
  Je("$$ms-gr-react-wrapper", p), Be(() => {
    m.set(X(t));
  }), qe(() => {
    h.forEach((a) => a());
  });
  function w(a) {
    H[a ? "unshift" : "push"](() => {
      i = a, g.set(i);
    });
  }
  function I(a) {
    H[a ? "unshift" : "push"](() => {
      s = a, c.set(s);
    });
  }
  return e.$$set = (a) => {
    o(17, t = U(U({}, t), q(a))), "svelteInit" in a && o(5, u = a.svelteInit), "$$scope" in a && o(6, r = a.$$scope);
  }, t = q(t), [i, s, g, c, l, u, r, n, w, I];
}
class Ze extends Pe {
  constructor(t) {
    super(), ze(this, t, Ye, Xe, De, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: st
} = window.__gradio__svelte__internal, Y = window.ms_globals.rerender, N = window.ms_globals.tree;
function Ke(e, t = {}) {
  function o(i) {
    const s = T(), n = new Ze({
      ...i,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: e,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: t.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, u = r.parent ?? N;
          return u.nodes = [...u.nodes, l], Y({
            createPortal: A,
            node: N
          }), r.onDestroy(() => {
            u.nodes = u.nodes.filter((m) => m.svelteInstance !== s), Y({
              createPortal: A,
              node: N
            });
          }), l;
        },
        ...i.props
      }
    });
    return s.set(n), n;
  }
  return new Promise((i) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((s) => {
      window.ms_globals.initialize = () => {
        s();
      };
    })), window.ms_globals.initializePromise.then(() => {
      i(o);
    });
  });
}
const Qe = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Ve(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const i = e[o];
    return t[o] = $e(o, i), t;
  }, {}) : {};
}
function $e(e, t) {
  return typeof t == "number" && !Qe.includes(e) ? t + "px" : t;
}
function j(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const s = E.Children.toArray(e._reactElement.props.children).map((n) => {
      if (E.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = j(n.props.el);
        return E.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...E.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return s.originalChildren = e._reactElement.props.children, t.push(A(E.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: s
    }), o)), {
      clonedElement: o,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((s) => {
    e.getEventListeners(s).forEach(({
      listener: r,
      type: l,
      useCapture: u
    }) => {
      o.addEventListener(l, r, u);
    });
  });
  const i = Array.from(e.childNodes);
  for (let s = 0; s < i.length; s++) {
    const n = i[s];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = j(n);
      t.push(...l), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: t
  };
}
function et(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const Z = re(({
  slot: e,
  clone: t,
  className: o,
  style: i,
  observeAttributes: s
}, n) => {
  const r = oe(), [l, u] = se([]), {
    forceClone: m
  } = de(), g = m ? !0 : t;
  return K(() => {
    var v;
    if (!r.current || !e)
      return;
    let c = e;
    function h() {
      let f = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (f = c.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), et(n, f), o && f.classList.add(...o.split(" ")), i) {
        const p = Ve(i);
        Object.keys(p).forEach((w) => {
          f.style[w] = p[w];
        });
      }
    }
    let _ = null, b = null;
    if (g && window.MutationObserver) {
      let f = function() {
        var a, x, d;
        (a = r.current) != null && a.contains(c) && ((x = r.current) == null || x.removeChild(c));
        const {
          portals: w,
          clonedElement: I
        } = j(e);
        c = I, u(w), c.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          h();
        }, 50), (d = r.current) == null || d.appendChild(c);
      };
      f();
      const p = Ce(() => {
        f(), _ == null || _.disconnect(), _ == null || _.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: s
        });
      }, 50);
      _ = new window.MutationObserver(p), _.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", h(), (v = r.current) == null || v.appendChild(c);
    return () => {
      var f, p;
      c.style.display = "", (f = r.current) != null && f.contains(c) && ((p = r.current) == null || p.removeChild(c)), _ == null || _.disconnect();
    };
  }, [e, g, o, i, n, s, m]), E.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
});
function tt(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function nt(e, t = !1) {
  try {
    if (ue(e))
      return e;
    if (t && !tt(e))
      return;
    if (typeof e == "string") {
      let o = e.trim();
      return o.startsWith(";") && (o = o.slice(1)), o.endsWith(";") && (o = o.slice(0, -1)), new Function(`return (...args) => (${o})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function rt(e, t) {
  return ie(() => nt(e, t), [e, t]);
}
const it = Ke(({
  slots: e,
  children: t,
  visible: o,
  onVisible: i,
  onClose: s,
  getContainer: n,
  messageKey: r,
  ...l
}) => {
  const u = rt(n), [m, g] = fe.useMessage({
    ...l,
    getContainer: u
  });
  return K(() => (o ? m.open({
    ...l,
    key: r,
    icon: e.icon ? /* @__PURE__ */ R.jsx(Z, {
      slot: e.icon
    }) : l.icon,
    content: e.content ? /* @__PURE__ */ R.jsx(Z, {
      slot: e.content
    }) : l.content,
    onClose(...c) {
      i == null || i(!1), s == null || s(...c);
    }
  }) : m.destroy(r), () => {
    m.destroy(r);
  }), [o, r, l.content, l.className, l.duration, l.icon, l.style, l.type]), /* @__PURE__ */ R.jsxs(R.Fragment, {
    children: [/* @__PURE__ */ R.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), g]
  });
});
export {
  it as Message,
  it as default
};
