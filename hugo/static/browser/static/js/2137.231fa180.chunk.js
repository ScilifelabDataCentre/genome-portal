"use strict";(globalThis.webpackChunk_jbrowse_web=globalThis.webpackChunk_jbrowse_web||[]).push([[2137],{62137:(e,t,o)=>{o.r(t),o.d(t,{default:()=>p});var n=o(66204),a=o(43902),r=o(29520),s=o(27513),l=o(49140),c=o(94926),i=o(73689),d=o(39780),u=o(32842),h=o(54899);function m({onClose:e,open:t}){return n.createElement(a.Dialog,{onClose:()=>e(),open:t,title:"Info about session URLs"},n.createElement(r.Z,null,n.createElement(s.Z,null,"Because everything about the JBrowse session is encoded in the URL (e.g. state of the tracks, views, features selected, etc.) the sessions can get very long. Therefore, we created a URL shortener, both as a convenience and because long URLs can break some programs. Note that both the long and short URLs encode the same data, but due to long URLs causing problems with some programs, we recommend sharing short URLs."),n.createElement(s.Z,null,'We generate the short URLs in a secure manner which involves encrypting the session on the client side with a random password string and uploading them to a central database. Then the random password is added to the URL but is not uploaded to the central database, making these short URLs effectively "end-to-end encrypted"'),n.createElement(s.Z,null,"Only users with a share link can read the session.")))}const Z="jbrowse-shareURL";function p(e){const{onClose:t,open:o,currentSetting:p}=e,[v,g]=(0,n.useState)(p),[f,b]=(0,n.useState)(!1);return n.createElement(n.Fragment,null,n.createElement(a.Dialog,{onClose:()=>{localStorage.setItem(Z,v),t(v)},open:o,title:"Configure session sharing"},n.createElement(r.Z,null,n.createElement(s.Z,null,"Select between generating long or short URLs for the session sharing",n.createElement(l.Z,{onClick:()=>b(!0)},n.createElement(h.Z,null))),n.createElement(c.Z,{component:"fieldset"},n.createElement(i.Z,{value:v,onChange:e=>g(e.target.value)},n.createElement(d.Z,{value:"short",control:n.createElement(u.Z,null),label:"Short URL"}),n.createElement(d.Z,{value:"long",control:n.createElement(u.Z,null),label:"Long URL"}))))),n.createElement(m,{open:f,onClose:()=>b(!1)}))}},54899:(e,t,o)=>{var n=o(57739);t.Z=void 0;var a=n(o(53948)),r=o(43188),s=(0,a.default)((0,r.jsx)("path",{d:"M11 18h2v-2h-2v2zm1-16C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4h2c0-1.1.9-2 2-2s2 .9 2 2c0 2-3 1.75-3 5h2c0-2.25 3-2.5 3-5 0-2.21-1.79-4-4-4z"}),"HelpOutline");t.Z=s},32842:(e,t,o)=>{o.d(t,{Z:()=>j});var n=o(55559),a=o(30984),r=o(66204),s=o(56317),l=o(58029),c=o(73330),i=o(68892),d=o(57369),u=o(50968),h=o(43188);const m=(0,u.Z)((0,h.jsx)("path",{d:"M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"}),"RadioButtonUnchecked"),Z=(0,u.Z)((0,h.jsx)("path",{d:"M8.465 8.465C9.37 7.56 10.62 7 12 7C14.76 7 17 9.24 17 12C17 13.38 16.44 14.63 15.535 15.535C14.63 16.44 13.38 17 12 17C9.24 17 7 14.76 7 12C7 10.62 7.56 9.37 8.465 8.465Z"}),"RadioButtonChecked");var p=o(61125);const v=(0,p.ZP)("span",{shouldForwardProp:p.FO})({position:"relative",display:"flex"}),g=(0,p.ZP)(m)({transform:"scale(1)"}),f=(0,p.ZP)(Z)((({theme:e,ownerState:t})=>(0,a.Z)({left:0,position:"absolute",transform:"scale(0)",transition:e.transitions.create("transform",{easing:e.transitions.easing.easeIn,duration:e.transitions.duration.shortest})},t.checked&&{transform:"scale(1)",transition:e.transitions.create("transform",{easing:e.transitions.easing.easeOut,duration:e.transitions.duration.shortest})}))),b=function(e){const{checked:t=!1,classes:o={},fontSize:n}=e,r=(0,a.Z)({},e,{checked:t});return(0,h.jsxs)(v,{className:o.root,ownerState:r,children:[(0,h.jsx)(g,{fontSize:n,className:o.background,ownerState:r}),(0,h.jsx)(f,{fontSize:n,className:o.dot,ownerState:r})]})};var C=o(40118),w=o(91882),S=o(66021),k=o(95474);const R=["checked","checkedIcon","color","icon","name","onChange","size","className"],z=(0,p.ZP)(i.Z,{shouldForwardProp:e=>(0,p.FO)(e)||"classes"===e,name:"MuiRadio",slot:"Root",overridesResolver:(e,t)=>{const{ownerState:o}=e;return[t.root,"medium"!==o.size&&t[`size${(0,C.Z)(o.size)}`],t[`color${(0,C.Z)(o.color)}`]]}})((({theme:e,ownerState:t})=>(0,a.Z)({color:(e.vars||e).palette.text.secondary},!t.disableRipple&&{"&:hover":{backgroundColor:e.vars?`rgba(${"default"===t.color?e.vars.palette.action.activeChannel:e.vars.palette[t.color].mainChannel} / ${e.vars.palette.action.hoverOpacity})`:(0,c.Fq)("default"===t.color?e.palette.action.active:e.palette[t.color].main,e.palette.action.hoverOpacity),"@media (hover: none)":{backgroundColor:"transparent"}}},"default"!==t.color&&{[`&.${k.Z.checked}`]:{color:(e.vars||e).palette[t.color].main}},{[`&.${k.Z.disabled}`]:{color:(e.vars||e).palette.action.disabled}}))),E=(0,h.jsx)(b,{checked:!0}),y=(0,h.jsx)(b,{}),j=r.forwardRef((function(e,t){var o,c;const i=(0,d.Z)({props:e,name:"MuiRadio"}),{checked:u,checkedIcon:m=E,color:Z="primary",icon:p=y,name:v,onChange:g,size:f="medium",className:b}=i,j=(0,n.Z)(i,R),x=(0,a.Z)({},i,{color:Z,size:f}),L=(e=>{const{classes:t,color:o,size:n}=e,r={root:["root",`color${(0,C.Z)(o)}`,"medium"!==n&&`size${(0,C.Z)(n)}`]};return(0,a.Z)({},t,(0,l.Z)(r,k.l,t))})(x),U=(0,S.Z)();let M=u;const P=(0,w.Z)(g,U&&U.onChange);let $=v;var I,N;return U&&(void 0===M&&(I=U.value,M="object"==typeof(N=i.value)&&null!==N?I===N:String(I)===String(N)),void 0===$&&($=U.name)),(0,h.jsx)(z,(0,a.Z)({type:"radio",icon:r.cloneElement(p,{fontSize:null!=(o=y.props.fontSize)?o:f}),checkedIcon:r.cloneElement(m,{fontSize:null!=(c=E.props.fontSize)?c:f}),ownerState:x,classes:L,name:$,checked:M,onChange:P,ref:t,className:(0,s.Z)(L.root,b)},j))}))},95474:(e,t,o)=>{o.d(t,{Z:()=>s,l:()=>r});var n=o(58109),a=o(95201);function r(e){return(0,a.Z)("MuiRadio",e)}const s=(0,n.Z)("MuiRadio",["root","checked","disabled","colorPrimary","colorSecondary","sizeSmall"])},73689:(e,t,o)=>{o.d(t,{Z:()=>m});var n=o(30984),a=o(55559),r=o(66204),s=o(53447),l=o(81597),c=o(24842),i=o(54855),d=o(79673),u=o(43188);const h=["actions","children","defaultValue","name","onChange","value"],m=r.forwardRef((function(e,t){const{actions:o,children:m,defaultValue:Z,name:p,onChange:v,value:g}=e,f=(0,a.Z)(e,h),b=r.useRef(null),[C,w]=(0,c.Z)({controlled:g,default:Z,name:"RadioGroup"});r.useImperativeHandle(o,(()=>({focus:()=>{let e=b.current.querySelector("input:not(:disabled):checked");e||(e=b.current.querySelector("input:not(:disabled)")),e&&e.focus()}})),[]);const S=(0,l.Z)(t,b),k=(0,d.Z)(p),R=r.useMemo((()=>({name:k,onChange(e){w(e.target.value),v&&v(e,e.target.value)},value:C})),[k,v,w,C]);return(0,u.jsx)(i.Z.Provider,{value:R,children:(0,u.jsx)(s.Z,(0,n.Z)({role:"radiogroup",ref:S},f,{children:m}))})}))},54855:(e,t,o)=>{o.d(t,{Z:()=>n});const n=o(66204).createContext(void 0)},66021:(e,t,o)=>{o.d(t,{Z:()=>r});var n=o(66204),a=o(54855);function r(){return n.useContext(a.Z)}}}]);
//# sourceMappingURL=2137.231fa180.chunk.js.map