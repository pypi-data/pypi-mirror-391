import { i as ce, a as W, r as ae, Z as T, g as ue, b as fe } from "./Index-CFpj3ADF.js";
const b = window.ms_globals.React, re = window.ms_globals.React.forwardRef, ie = window.ms_globals.React.useRef, oe = window.ms_globals.React.useState, se = window.ms_globals.React.useEffect, le = window.ms_globals.React.useMemo, N = window.ms_globals.ReactDOM.createPortal, de = window.ms_globals.internalContext.useContextPropsContext, me = window.ms_globals.internalContext.ContextPropsProvider, _e = window.ms_globals.antd.Statistic;
var he = /\s/;
function pe(t) {
  for (var e = t.length; e-- && he.test(t.charAt(e)); )
    ;
  return e;
}
var ge = /^\s+/;
function we(t) {
  return t && t.slice(0, pe(t) + 1).replace(ge, "");
}
var D = NaN, xe = /^[-+]0x[0-9a-f]+$/i, be = /^0b[01]+$/i, ye = /^0o[0-7]+$/i, ve = parseInt;
function U(t) {
  if (typeof t == "number")
    return t;
  if (ce(t))
    return D;
  if (W(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = W(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = we(t);
  var i = be.test(t);
  return i || ye.test(t) ? ve(t.slice(2), i ? 2 : 8) : xe.test(t) ? D : +t;
}
var L = function() {
  return ae.Date.now();
}, Ce = "Expected a function", Ee = Math.max, Se = Math.min;
function Ie(t, e, i) {
  var s, o, n, r, l, f, p = 0, g = !1, c = !1, w = !0;
  if (typeof t != "function")
    throw new TypeError(Ce);
  e = U(e) || 0, W(i) && (g = !!i.leading, c = "maxWait" in i, n = c ? Ee(U(i.maxWait) || 0, e) : n, w = "trailing" in i ? !!i.trailing : w);
  function m(u) {
    var y = s, P = o;
    return s = o = void 0, p = u, r = t.apply(P, y), r;
  }
  function v(u) {
    return p = u, l = setTimeout(h, e), g ? m(u) : r;
  }
  function C(u) {
    var y = u - f, P = u - p, z = e - y;
    return c ? Se(z, n - P) : z;
  }
  function d(u) {
    var y = u - f, P = u - p;
    return f === void 0 || y >= e || y < 0 || c && P >= n;
  }
  function h() {
    var u = L();
    if (d(u))
      return x(u);
    l = setTimeout(h, C(u));
  }
  function x(u) {
    return l = void 0, w && s ? m(u) : (s = o = void 0, r);
  }
  function I() {
    l !== void 0 && clearTimeout(l), p = 0, s = f = o = l = void 0;
  }
  function a() {
    return l === void 0 ? r : x(L());
  }
  function E() {
    var u = L(), y = d(u);
    if (s = arguments, o = this, f = u, y) {
      if (l === void 0)
        return v(f);
      if (c)
        return clearTimeout(l), l = setTimeout(h, e), m(f);
    }
    return l === void 0 && (l = setTimeout(h, e)), r;
  }
  return E.cancel = I, E.flush = a, E;
}
var Z = {
  exports: {}
}, j = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Pe = b, Re = Symbol.for("react.element"), Te = Symbol.for("react.fragment"), Oe = Object.prototype.hasOwnProperty, ke = Pe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, je = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Q(t, e, i) {
  var s, o = {}, n = null, r = null;
  i !== void 0 && (n = "" + i), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (r = e.ref);
  for (s in e) Oe.call(e, s) && !je.hasOwnProperty(s) && (o[s] = e[s]);
  if (t && t.defaultProps) for (s in e = t.defaultProps, e) o[s] === void 0 && (o[s] = e[s]);
  return {
    $$typeof: Re,
    type: t,
    key: n,
    ref: r,
    props: o,
    _owner: ke.current
  };
}
j.Fragment = Te;
j.jsx = Q;
j.jsxs = Q;
Z.exports = j;
var _ = Z.exports;
const {
  SvelteComponent: Le,
  assign: B,
  binding_callbacks: G,
  check_outros: Fe,
  children: $,
  claim_element: ee,
  claim_space: Ne,
  component_subscribe: H,
  compute_slots: We,
  create_slot: Ae,
  detach: S,
  element: te,
  empty: K,
  exclude_internal_props: q,
  get_all_dirty_from_scope: Me,
  get_slot_changes: ze,
  group_outros: De,
  init: Ue,
  insert_hydration: O,
  safe_not_equal: Be,
  set_custom_element_data: ne,
  space: Ge,
  transition_in: k,
  transition_out: A,
  update_slot_base: He
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ke,
  getContext: qe,
  onDestroy: Ve,
  setContext: Je
} = window.__gradio__svelte__internal;
function V(t) {
  let e, i;
  const s = (
    /*#slots*/
    t[7].default
  ), o = Ae(
    s,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = te("svelte-slot"), o && o.c(), this.h();
    },
    l(n) {
      e = ee(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = $(e);
      o && o.l(r), r.forEach(S), this.h();
    },
    h() {
      ne(e, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      O(n, e, r), o && o.m(e, null), t[9](e), i = !0;
    },
    p(n, r) {
      o && o.p && (!i || r & /*$$scope*/
      64) && He(
        o,
        s,
        n,
        /*$$scope*/
        n[6],
        i ? ze(
          s,
          /*$$scope*/
          n[6],
          r,
          null
        ) : Me(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      i || (k(o, n), i = !0);
    },
    o(n) {
      A(o, n), i = !1;
    },
    d(n) {
      n && S(e), o && o.d(n), t[9](null);
    }
  };
}
function Xe(t) {
  let e, i, s, o, n = (
    /*$$slots*/
    t[4].default && V(t)
  );
  return {
    c() {
      e = te("react-portal-target"), i = Ge(), n && n.c(), s = K(), this.h();
    },
    l(r) {
      e = ee(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), $(e).forEach(S), i = Ne(r), n && n.l(r), s = K(), this.h();
    },
    h() {
      ne(e, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      O(r, e, l), t[8](e), O(r, i, l), n && n.m(r, l), O(r, s, l), o = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && k(n, 1)) : (n = V(r), n.c(), k(n, 1), n.m(s.parentNode, s)) : n && (De(), A(n, 1, 1, () => {
        n = null;
      }), Fe());
    },
    i(r) {
      o || (k(n), o = !0);
    },
    o(r) {
      A(n), o = !1;
    },
    d(r) {
      r && (S(e), S(i), S(s)), t[8](null), n && n.d(r);
    }
  };
}
function J(t) {
  const {
    svelteInit: e,
    ...i
  } = t;
  return i;
}
function Ye(t, e, i) {
  let s, o, {
    $$slots: n = {},
    $$scope: r
  } = e;
  const l = We(n);
  let {
    svelteInit: f
  } = e;
  const p = T(J(e)), g = T();
  H(t, g, (a) => i(0, s = a));
  const c = T();
  H(t, c, (a) => i(1, o = a));
  const w = [], m = qe("$$ms-gr-react-wrapper"), {
    slotKey: v,
    slotIndex: C,
    subSlotIndex: d
  } = ue() || {}, h = f({
    parent: m,
    props: p,
    target: g,
    slot: c,
    slotKey: v,
    slotIndex: C,
    subSlotIndex: d,
    onDestroy(a) {
      w.push(a);
    }
  });
  Je("$$ms-gr-react-wrapper", h), Ke(() => {
    p.set(J(e));
  }), Ve(() => {
    w.forEach((a) => a());
  });
  function x(a) {
    G[a ? "unshift" : "push"](() => {
      s = a, g.set(s);
    });
  }
  function I(a) {
    G[a ? "unshift" : "push"](() => {
      o = a, c.set(o);
    });
  }
  return t.$$set = (a) => {
    i(17, e = B(B({}, e), q(a))), "svelteInit" in a && i(5, f = a.svelteInit), "$$scope" in a && i(6, r = a.$$scope);
  }, e = q(e), [s, o, g, c, l, f, r, n, x, I];
}
class Ze extends Le {
  constructor(e) {
    super(), Ue(this, e, Ye, Xe, Be, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ut
} = window.__gradio__svelte__internal, X = window.ms_globals.rerender, F = window.ms_globals.tree;
function Qe(t, e = {}) {
  function i(s) {
    const o = T(), n = new Ze({
      ...s,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: t,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: e.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, f = r.parent ?? F;
          return f.nodes = [...f.nodes, l], X({
            createPortal: N,
            node: F
          }), r.onDestroy(() => {
            f.nodes = f.nodes.filter((p) => p.svelteInstance !== o), X({
              createPortal: N,
              node: F
            });
          }), l;
        },
        ...s.props
      }
    });
    return o.set(n), n;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((o) => {
      window.ms_globals.initialize = () => {
        o();
      };
    })), window.ms_globals.initializePromise.then(() => {
      s(i);
    });
  });
}
const $e = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function et(t) {
  return t ? Object.keys(t).reduce((e, i) => {
    const s = t[i];
    return e[i] = tt(i, s), e;
  }, {}) : {};
}
function tt(t, e) {
  return typeof e == "number" && !$e.includes(t) ? e + "px" : e;
}
function M(t) {
  const e = [], i = t.cloneNode(!1);
  if (t._reactElement) {
    const o = b.Children.toArray(t._reactElement.props.children).map((n) => {
      if (b.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = M(n.props.el);
        return b.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...b.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return o.originalChildren = t._reactElement.props.children, e.push(N(b.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: o
    }), i)), {
      clonedElement: i,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((o) => {
    t.getEventListeners(o).forEach(({
      listener: r,
      type: l,
      useCapture: f
    }) => {
      i.addEventListener(l, r, f);
    });
  });
  const s = Array.from(t.childNodes);
  for (let o = 0; o < s.length; o++) {
    const n = s[o];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = M(n);
      e.push(...l), i.appendChild(r);
    } else n.nodeType === 3 && i.appendChild(n.cloneNode());
  }
  return {
    clonedElement: i,
    portals: e
  };
}
function nt(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const R = re(({
  slot: t,
  clone: e,
  className: i,
  style: s,
  observeAttributes: o
}, n) => {
  const r = ie(), [l, f] = oe([]), {
    forceClone: p
  } = de(), g = p ? !0 : e;
  return se(() => {
    var C;
    if (!r.current || !t)
      return;
    let c = t;
    function w() {
      let d = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (d = c.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), nt(n, d), i && d.classList.add(...i.split(" ")), s) {
        const h = et(s);
        Object.keys(h).forEach((x) => {
          d.style[x] = h[x];
        });
      }
    }
    let m = null, v = null;
    if (g && window.MutationObserver) {
      let d = function() {
        var a, E, u;
        (a = r.current) != null && a.contains(c) && ((E = r.current) == null || E.removeChild(c));
        const {
          portals: x,
          clonedElement: I
        } = M(t);
        c = I, f(x), c.style.display = "contents", v && clearTimeout(v), v = setTimeout(() => {
          w();
        }, 50), (u = r.current) == null || u.appendChild(c);
      };
      d();
      const h = Ie(() => {
        d(), m == null || m.disconnect(), m == null || m.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      m = new window.MutationObserver(h), m.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", w(), (C = r.current) == null || C.appendChild(c);
    return () => {
      var d, h;
      c.style.display = "", (d = r.current) != null && d.contains(c) && ((h = r.current) == null || h.removeChild(c)), m == null || m.disconnect();
    };
  }, [t, g, i, s, n, o, p]), b.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
});
function rt(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function it(t, e = !1) {
  try {
    if (fe(t))
      return t;
    if (e && !rt(t))
      return;
    if (typeof t == "string") {
      let i = t.trim();
      return i.startsWith(";") && (i = i.slice(1)), i.endsWith(";") && (i = i.slice(0, -1)), new Function(`return (...args) => (${i})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function ot(t, e) {
  return le(() => it(t, e), [t, e]);
}
const st = ({
  children: t,
  ...e
}) => /* @__PURE__ */ _.jsx(_.Fragment, {
  children: t(e)
});
function lt(t) {
  return b.createElement(st, {
    children: t
  });
}
function Y(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? lt((i) => /* @__PURE__ */ _.jsx(me, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ _.jsx(R, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...i
    })
  })) : /* @__PURE__ */ _.jsx(R, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function ct({
  key: t,
  slots: e,
  targets: i
}, s) {
  return e[t] ? (...o) => i ? i.map((n, r) => /* @__PURE__ */ _.jsx(b.Fragment, {
    children: Y(n, {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }, r)) : /* @__PURE__ */ _.jsx(_.Fragment, {
    children: Y(e[t], {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }) : void 0;
}
const ft = Qe(({
  children: t,
  slots: e,
  setSlotParams: i,
  formatter: s,
  ...o
}) => {
  const n = ot(s);
  return /* @__PURE__ */ _.jsxs(_.Fragment, {
    children: [/* @__PURE__ */ _.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ _.jsx(_e, {
      ...o,
      formatter: e.formatter ? ct({
        slots: e,
        key: "formatter"
      }) : n,
      title: e.title ? /* @__PURE__ */ _.jsx(R, {
        slot: e.title
      }) : o.title,
      prefix: e.prefix ? /* @__PURE__ */ _.jsx(R, {
        slot: e.prefix
      }) : o.prefix,
      suffix: e.suffix ? /* @__PURE__ */ _.jsx(R, {
        slot: e.suffix
      }) : o.suffix
    })]
  });
});
export {
  ft as Statistic,
  ft as default
};
