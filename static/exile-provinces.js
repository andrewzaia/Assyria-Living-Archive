/* Progressive evidence filters: all case content is visible without JavaScript. */
(function(){
  "use strict";
  const root=document.querySelector(".exile-room");
  if(!root)return;
  const controls=[...root.querySelectorAll("[data-exile-filter]")];
  const studies=[...root.querySelectorAll("[data-exile-category]")];
  const status=root.querySelector(".exile-filter-count");
  const filter=(category)=>{
    let shown=0;
    for(const item of studies){item.hidden=!(category==="all"||item.dataset.exileCategory===category);if(!item.hidden)shown++;}
    for(const button of controls)button.setAttribute("aria-pressed",String(button.dataset.exileFilter===category));
    if(status)status.textContent=shown+(shown===1?" study displayed":" studies displayed");
  };
  for(const button of controls)button.addEventListener("click",()=>filter(button.dataset.exileFilter));
  window.addEventListener("hashchange",()=>{if(studies.some(s=>"#"+s.id===location.hash))filter("all");});
})();
