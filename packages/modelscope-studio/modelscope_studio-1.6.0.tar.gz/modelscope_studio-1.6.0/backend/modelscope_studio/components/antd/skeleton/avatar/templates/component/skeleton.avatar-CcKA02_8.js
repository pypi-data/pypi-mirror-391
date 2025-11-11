import { Z as m, g as N } from "./Index-QFZokrwn.js";
const v = window.ms_globals.ReactDOM.createPortal, U = window.ms_globals.antd.Skeleton, {
  SvelteComponent: V,
  assign: I,
  binding_callbacks: k,
  check_outros: W,
  children: A,
  claim_element: R,
  claim_space: Z,
  component_subscribe: S,
  compute_slots: j,
  create_slot: B,
  detach: _,
  element: z,
  empty: y,
  exclude_internal_props: P,
  get_all_dirty_from_scope: F,
  get_slot_changes: H,
  group_outros: J,
  init: Q,
  insert_hydration: p,
  safe_not_equal: X,
  set_custom_element_data: D,
  space: Y,
  transition_in: g,
  transition_out: b,
  update_slot_base: $
} = window.__gradio__svelte__internal, {
  beforeUpdate: ee,
  getContext: te,
  onDestroy: se,
  setContext: oe
} = window.__gradio__svelte__internal;
function C(r) {
  let s, n;
  const l = (
    /*#slots*/
    r[7].default
  ), o = B(
    l,
    r,
    /*$$scope*/
    r[6],
    null
  );
  return {
    c() {
      s = z("svelte-slot"), o && o.c(), this.h();
    },
    l(e) {
      s = R(e, "SVELTE-SLOT", {
        class: !0
      });
      var t = A(s);
      o && o.l(t), t.forEach(_), this.h();
    },
    h() {
      D(s, "class", "svelte-1rt0kpf");
    },
    m(e, t) {
      p(e, s, t), o && o.m(s, null), r[9](s), n = !0;
    },
    p(e, t) {
      o && o.p && (!n || t & /*$$scope*/
      64) && $(
        o,
        l,
        e,
        /*$$scope*/
        e[6],
        n ? H(
          l,
          /*$$scope*/
          e[6],
          t,
          null
        ) : F(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      n || (g(o, e), n = !0);
    },
    o(e) {
      b(o, e), n = !1;
    },
    d(e) {
      e && _(s), o && o.d(e), r[9](null);
    }
  };
}
function ne(r) {
  let s, n, l, o, e = (
    /*$$slots*/
    r[4].default && C(r)
  );
  return {
    c() {
      s = z("react-portal-target"), n = Y(), e && e.c(), l = y(), this.h();
    },
    l(t) {
      s = R(t, "REACT-PORTAL-TARGET", {
        class: !0
      }), A(s).forEach(_), n = Z(t), e && e.l(t), l = y(), this.h();
    },
    h() {
      D(s, "class", "svelte-1rt0kpf");
    },
    m(t, a) {
      p(t, s, a), r[8](s), p(t, n, a), e && e.m(t, a), p(t, l, a), o = !0;
    },
    p(t, [a]) {
      /*$$slots*/
      t[4].default ? e ? (e.p(t, a), a & /*$$slots*/
      16 && g(e, 1)) : (e = C(t), e.c(), g(e, 1), e.m(l.parentNode, l)) : e && (J(), b(e, 1, 1, () => {
        e = null;
      }), W());
    },
    i(t) {
      o || (g(e), o = !0);
    },
    o(t) {
      b(e), o = !1;
    },
    d(t) {
      t && (_(s), _(n), _(l)), r[8](null), e && e.d(t);
    }
  };
}
function E(r) {
  const {
    svelteInit: s,
    ...n
  } = r;
  return n;
}
function le(r, s, n) {
  let l, o, {
    $$slots: e = {},
    $$scope: t
  } = s;
  const a = j(e);
  let {
    svelteInit: c
  } = s;
  const u = m(E(s)), f = m();
  S(r, f, (i) => n(0, l = i));
  const d = m();
  S(r, d, (i) => n(1, o = i));
  const h = [], K = te("$$ms-gr-react-wrapper"), {
    slotKey: L,
    slotIndex: O,
    subSlotIndex: x
  } = N() || {}, q = c({
    parent: K,
    props: u,
    target: f,
    slot: d,
    slotKey: L,
    slotIndex: O,
    subSlotIndex: x,
    onDestroy(i) {
      h.push(i);
    }
  });
  oe("$$ms-gr-react-wrapper", q), ee(() => {
    u.set(E(s));
  }), se(() => {
    h.forEach((i) => i());
  });
  function G(i) {
    k[i ? "unshift" : "push"](() => {
      l = i, f.set(l);
    });
  }
  function M(i) {
    k[i ? "unshift" : "push"](() => {
      o = i, d.set(o);
    });
  }
  return r.$$set = (i) => {
    n(17, s = I(I({}, s), P(i))), "svelteInit" in i && n(5, c = i.svelteInit), "$$scope" in i && n(6, t = i.$$scope);
  }, s = P(s), [l, o, f, d, a, c, t, e, G, M];
}
class re extends V {
  constructor(s) {
    super(), Q(this, s, le, ne, X, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ce
} = window.__gradio__svelte__internal, T = window.ms_globals.rerender, w = window.ms_globals.tree;
function ie(r, s = {}) {
  function n(l) {
    const o = m(), e = new re({
      ...l,
      props: {
        svelteInit(t) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: r,
            props: t.props,
            slot: t.slot,
            target: t.target,
            slotIndex: t.slotIndex,
            subSlotIndex: t.subSlotIndex,
            ignore: s.ignore,
            slotKey: t.slotKey,
            nodes: []
          }, c = t.parent ?? w;
          return c.nodes = [...c.nodes, a], T({
            createPortal: v,
            node: w
          }), t.onDestroy(() => {
            c.nodes = c.nodes.filter((u) => u.svelteInstance !== o), T({
              createPortal: v,
              node: w
            });
          }), a;
        },
        ...l.props
      }
    });
    return o.set(e), e;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((o) => {
      window.ms_globals.initialize = () => {
        o();
      };
    })), window.ms_globals.initializePromise.then(() => {
      l(n);
    });
  });
}
const _e = ie(U.Avatar);
export {
  _e as SkeletonAvatar,
  _e as default
};
