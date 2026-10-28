(() => { const poses=['idle','armsUp','crossed','hands-on-head','ball','point'];
 const kits=["coach","barca","red","realAway","gk","flamengo"];
 window.EPISODE={handle:'seu.perfil',scenes:[{dur:3,chrome:false,draw:(t,a)=>{const {C}=a; let s=C.floor(1500)+'';
   kits.forEach((k,i)=>{ const col=i%3,row=Math.floor(i/3); s+=C.figure(190+col*350,720+row*760,C.kits[k],{pose:poses[i],scale:.6,t:0,bob:false,label:k+' · '+poses[i]});});
   return s.replace(/<rect x="0" y="1500"[^]*?<\/rect>/,'');}}]};})();
