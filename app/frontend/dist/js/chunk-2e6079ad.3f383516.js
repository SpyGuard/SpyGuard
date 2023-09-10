(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-2e6079ad"],{"1d0d":function(t,e){t.exports=function(t){var e={};function r(n){if(e[n])return e[n].exports;var i=e[n]={i:n,l:!1,exports:{}};return t[n].call(i.exports,i,i.exports,r),i.l=!0,i.exports}return r.m=t,r.c=e,r.d=function(t,e,n){r.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:n})},r.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},r.t=function(t,e){if(1&e&&(t=r(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var n=Object.create(null);if(r.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var i in t)r.d(n,i,function(e){return t[e]}.bind(null,i));return n},r.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return r.d(e,"a",e),e},r.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},r.p="",r(r.s=1)}([function(t,e,r){var n=r(2),i=r(3),s=r(4);t.exports=function(t){return n(t)||i(t)||s()}},function(t,e,r){"use strict";r.r(e),r.d(e,"sparkline",(function(){return c}));var n=r(0),i=r.n(n);function s(t,e,r,n){return parseFloat((e-n*e/t+r).toFixed(2))}function a(t){return t.value}function o(t,e){var r=document.createElementNS("http://www.w3.org/2000/svg",t);for(var n in e)r.setAttribute(n,e[n]);return r}function c(t,e,r){var n;if(n=t,i()(n.querySelectorAll("*")).forEach((function(t){return n.removeChild(t)})),!(e.length<=1)){r=r||{},"number"==typeof e[0]&&(e=e.map((function(t){return{value:t}})));var c=r.onmousemove,u=r.onmouseout,l="interactive"in r?r.interactive:!!c,p=r.spotRadius||2,h=2*p,d=r.cursorWidth||2,f=parseFloat(t.attributes["stroke-width"].value),m=r.fetch||a,v=e.map((function(t){return m(t)})),_=parseFloat(t.attributes.width.value)-2*h,g=parseFloat(t.attributes.height.value),b=g-2*f-h,w=Math.max.apply(Math,i()(v)),y=-1e3,k=v.length-1,x=_/k,S=[],A=s(w,b,f+p,v[0]),j="M".concat(h," ").concat(A);v.forEach((function(t,r){var n=r*x+h,i=s(w,b,f+p,t);S.push(Object.assign({},e[r],{index:r,x:n,y:i})),j+=" L ".concat(n," ").concat(i)}));var C=o("path",{class:"sparkline--line",d:j,fill:"none"}),O=o("path",{class:"sparkline--fill",d:"".concat(j," V ").concat(g," L ").concat(h," ").concat(g," Z"),stroke:"none"});if(t.appendChild(O),t.appendChild(C),l){var M=o("line",{class:"sparkline--cursor",x1:y,x2:y,y1:0,y2:g,"stroke-width":d}),E=o("circle",{class:"sparkline--spot",cx:y,cy:y,r:p});t.appendChild(M),t.appendChild(E);var F=o("rect",{width:t.attributes.width.value,height:t.attributes.height.value,style:"fill: transparent; stroke: transparent",class:"sparkline--interaction-layer"});t.appendChild(F),F.addEventListener("mouseout",(function(t){M.setAttribute("x1",y),M.setAttribute("x2",y),E.setAttribute("cx",y),u&&u(t)})),F.addEventListener("mousemove",(function(t){var e=t.offsetX,r=S.find((function(t){return t.x>=e}));r||(r=S[k]);var n,i=S[S.indexOf(r)-1],s=(n=i?i.x+(r.x-i.x)/2<=e?r:i:r).x,a=n.y;E.setAttribute("cx",s),E.setAttribute("cy",a),M.setAttribute("x1",s),M.setAttribute("x2",s),c&&c(t,n)}))}}}e.default=c},function(t,e){t.exports=function(t){if(Array.isArray(t)){for(var e=0,r=new Array(t.length);e<t.length;e++)r[e]=t[e];return r}}},function(t,e){t.exports=function(t){if(Symbol.iterator in Object(t)||"[object Arguments]"===Object.prototype.toString.call(t))return Array.from(t)}},function(t,e){t.exports=function(){throw new TypeError("Invalid attempt to spread non-iterable instance")}}])},e583:function(t,e,r){"use strict";r.r(e);var n=function(){var t=this,e=t._self._c;return e("div",{staticClass:"wrapper"},[t.sparklines?e("svg",{attrs:{id:"sparkline","stroke-width":"3",width:t.sparkwidth,height:t.sparkheight}}):t._e(),e("div",{staticClass:"center"},[e("div",{staticClass:"footer"},[e("h3",{staticClass:"timer"},[t._v(t._s(t.timer_hours)+":"+t._s(t.timer_minutes)+":"+t._s(t.timer_seconds))]),e("p",[t._v(t._s(t.$t("capture.intercept_coms_msg"))+" "+t._s(t.device_name)+".")]),e("div",{staticClass:"empty-action"},[e("button",{staticClass:"btn btn-primary",on:{click:function(e){return t.stop_capture()}}},[t._v(t._s(t.$t("capture.stop_btn")))])])])])])},i=[],s=r("bc3a"),a=r.n(s),o=r("a18c"),c=r("1d0d"),u=r.n(c),l={name:"capture",components:{},data(){return{timer_hours:"00",timer_minutes:"00",timer_seconds:"00",stats_interval:!1,chrono_interval:!1,sparklines:!1}},props:{capture_token:String,device_name:String},methods:{set_chrono:function(){console.log("[capture.vue] Setting up the chrono"),this.chrono_interval=setInterval(()=>{this.chrono()},10)},stop_capture:function(){console.log("[capture.vue] Stoping the capture"),a.a.get("/api/capture/stop",{timeout:3e4}),clearInterval(this.chrono_interval),clearInterval(this.stats_interval),window.access_point="";var t=this.capture_token;o["a"].replace({name:"analysis",params:{capture_token:t}})},get_stats:function(){console.log("[capture.vue] Getting capture statistics"),a.a.get("/api/capture/stats",{timeout:3e4}).then(t=>this.handle_stats(t.data))},handle_stats:function(t){t.packets.length&&u()(document.querySelector("#sparkline"),t.packets)},chrono:function(){var t=Date.now()-this.capture_start;this.timer_hours=Math.floor(t/36e5),this.timer_hours=this.timer_hours<10?"0"+this.timer_hours:this.timer_hours,t%=36e5,this.timer_minutes=Math.floor(t/6e4),this.timer_minutes=this.timer_minutes<10?"0"+this.timer_minutes:this.timer_minutes,t%=6e4,this.timer_seconds=Math.floor(t/1e3),this.timer_seconds=this.timer_seconds<10?"0"+this.timer_seconds:this.timer_seconds},setup_sparklines:function(){a.a.get("/api/misc/config",{timeout:6e4}).then(t=>{t.data.sparklines&&(console.log("[capture.vue] Setting up sparklines"),this.sparklines=!0,this.sparkwidth=window.screen.width+"px",this.sparkheight=Math.trunc(window.screen.height/5)+"px",this.stats_interval=setInterval(()=>{this.get_stats()},500))}).catch(t=>{console.log(t)})}},created:function(){console.log("[capture.vue] Showing capture.vue"),this.setup_sparklines(),this.capture_start=Date.now(),this.set_chrono()}},p=l,h=r("2877"),d=Object(h["a"])(p,n,i,!1,null,null,null);e["default"]=d.exports}}]);
//# sourceMappingURL=chunk-2e6079ad.3f383516.js.map