const $ = selector => document.querySelector(selector);
const apps = [
  {id:'files',name:'Tệp',asset:'files',search:'tep files dolphin'},
  {id:'browser',name:'Trình duyệt',asset:'browser',search:'trinh duyet browser'},
  {id:'notes',name:'Ghi chú',asset:'notes',search:'ghi chu kate'},
  {id:'terminal',name:'Trình dòng lệnh',asset:'terminal',search:'terminal konsole dong lenh'},
  {id:'photos',name:'Hình ảnh',asset:'photos',search:'hinh anh gwenview'},
  {id:'settings',name:'Thiết lập',asset:'settings',search:'thiet lap settings'},
  {id:'workspace',name:'Workspace',asset:'notes',search:'workspace khong gian'}
];
const folders = {home:'Thư mục cá nhân',documents:'Tài liệu',downloads:'Tải xuống',pictures:'Hình ảnh',trash:'Thùng rác'};
const homeFolders = ['Tài liệu','Tải xuống','Hình ảnh','Âm nhạc','Video','Màn hình làm việc'];
let currentApp = null, folder = 'home', allApps = false;
const running = new Set();
function normalize(text) { return text.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d'); }
function closePopups() { if($('#launcher').open)$('#launcher').close();$('#notifications').hidden=true;$('#sound').hidden=true;$('#notificationsButton').setAttribute('aria-expanded','false');$('#soundButton').setAttribute('aria-expanded','false'); }
function renderTasks() { document.querySelectorAll('#tasks [data-app]').forEach(button=>{button.classList.toggle('running',running.has(button.dataset.app));button.classList.toggle('active',button.dataset.app===currentApp&&!$('#appWindow').hidden);}); }
function renderApps() {
  const query=normalize($('#appSearch').value);
  const visible=apps.filter(app=>(allApps||query||app.id!=='workspace')&&normalize(app.name+' '+app.search).includes(query));
  $('#appList').replaceChildren(...visible.map(app=>{const button=document.createElement('button');const image=document.createElement('img');image.src='../assets/app-icons/'+app.asset+'.svg';image.alt='';button.dataset.app=app.id;button.append(image,document.createTextNode(app.name));button.onclick=()=>openApp(app.id);return button;}));
  $('#emptySearch').hidden=visible.length>0;$('#appList').hidden=visible.length===0;
  $('#listTitle').textContent=query?'Kết quả tìm kiếm':(allApps?'Tất cả ứng dụng':'Đã ghim');
  $('#allApps').textContent=allApps?'Đã ghim':'Tất cả ứng dụng';
}
function openLauncher() { closePopups();$('#login').hidden=true;$('#appSearch').value='';allApps=false;renderApps();$('#launcher').showModal();$('#appSearch').focus(); }
function setFolder(id) { folder=id;$('#breadcrumb').textContent=folders[id];$('#fileSearch').value='';document.querySelectorAll('[data-folder]').forEach(button=>{if(button.dataset.folder===id)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');});renderFiles(); }
function renderFiles() {
  const names=folder==='home'?homeFolders:[];
  const filtered=names.filter(name=>normalize(name).includes(normalize($('#fileSearch').value)));
  $('#fileList').replaceChildren(...filtered.map(name=>{const button=document.createElement('button');button.className='file-row';const label=document.createElement('span');label.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><use href="../assets/icons/sprite.svg#files"/></svg>';label.append(document.createTextNode(name));const type=document.createElement('span');type.textContent='Thư mục';const size=document.createElement('span');size.textContent='—';button.append(label,type,size);button.onclick=()=>{document.querySelectorAll('.file-row').forEach(row=>row.classList.remove('selected'));button.classList.add('selected');};button.ondblclick=()=>setFolder({'Tài liệu':'documents','Tải xuống':'downloads','Hình ảnh':'pictures'}[name]||'documents');return button;}));
  $('#emptyFiles').hidden=filtered.length>0;$('#emptyFiles').textContent=names.length&&!filtered.length?'Không tìm thấy mục phù hợp':'Thư mục trống';$('#fileCount').textContent=filtered.length+' mục';
}
function openApp(id) {
  const app=apps.find(item=>item.id===id);if(!app)return;
  closePopups();$('#login').hidden=true;$('#loginMessage').textContent='';if(currentApp===id){$('#appWindow').hidden=false;renderTasks();return;}currentApp=id;running.add(id);$('#appWindow').hidden=false;$('#windowTitle').textContent=app.name;
  $('#filesView').hidden=id!=='files';$('#settingsView').hidden=id!=='settings';$('#simpleView').hidden=['files','settings'].includes(id);
  $('#simpleView').replaceChildren();$('#simpleView').className='simple-content';
  if(id==='files')setFolder(folder);
  if(id==='photos')$('#simpleView').textContent='Không có hình ảnh';
  if(id==='terminal')$('#simpleView').textContent='mykos@desktop:~$';
  if(id==='notes'){const area=document.createElement('textarea');area.setAttribute('aria-label','Ghi chú minh họa');area.style.cssText='width:100%;height:420px;border:0;background:transparent;color:inherit;font:inherit;resize:none;outline-offset:-3px';$('#simpleView').append(area);}
  if(id==='browser'){const address=document.createElement('input');address.placeholder='Địa chỉ web';address.setAttribute('aria-label','Địa chỉ web minh họa');address.readOnly=true;$('#simpleView').classList.add('browser');$('#simpleView').append(address);}
  if(id==='workspace'){$('#simpleView').textContent='';}
  renderTasks();$('#closeWindow').focus();
}
function showDesktop() { closePopups();$('#appWindow').hidden=true;$('#login').hidden=true;$('#password').value='';renderTasks(); }
function setTheme(theme) { document.body.dataset.theme=theme;document.querySelectorAll('[data-theme-choice]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.themeChoice===theme))); }
$('#launcherButton').onclick=openLauncher;$('#closeLauncher').onclick=()=>$('#launcher').close();$('#appSearch').oninput=renderApps;
$('#appSearch').onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();$('#appList button')?.click();}};
$('#allApps').onclick=()=>{allApps=!allApps;renderApps();};
document.querySelectorAll('#tasks [data-app]').forEach(button=>button.onclick=()=>{if(currentApp===button.dataset.app&&!$('#appWindow').hidden){$('#appWindow').hidden=true;renderTasks();}else openApp(button.dataset.app);});
$('#closeWindow').onclick=()=>{running.delete(currentApp);currentApp=null;$('#appWindow').hidden=true;renderTasks();$('#launcherButton').focus();};
$('#minimize').onclick=()=>{$('#appWindow').hidden=true;renderTasks();};$('#maximize').onclick=()=>$('#appWindow').classList.toggle('maximized');$('#showDesktop').onclick=showDesktop;
document.querySelectorAll('[data-folder]').forEach(button=>button.onclick=()=>setFolder(button.dataset.folder));$('#fileSearch').oninput=renderFiles;$('#back').onclick=()=>setFolder('home');
document.querySelectorAll('[data-theme-choice]').forEach(button=>button.onclick=()=>setTheme(button.dataset.themeChoice));$('#reducedMotion').onchange=event=>document.body.dataset.reducedMotion=String(event.target.checked);
$('#notificationsButton').onclick=()=>{const opening=$('#notifications').hidden;closePopups();$('#notifications').hidden=!opening;$('#notificationsButton').setAttribute('aria-expanded',String(opening));};$('#closeNotifications').onclick=closePopups;
$('#soundButton').onclick=()=>{const opening=$('#sound').hidden;closePopups();$('#sound').hidden=!opening;$('#soundButton').setAttribute('aria-expanded',String(opening));};$('#volume').oninput=event=>$('#volumeValue').textContent=event.target.value+'%';
$('#lock').onclick=()=>{closePopups();$('#login').hidden=false;$('#password').value='';$('#loginMessage').textContent='';$('#password').focus();};
$('#loginForm').onsubmit=event=>{event.preventDefault();$('#password').value='';$('#loginMessage').textContent='Bản mẫu không xác thực tài khoản.';};
$('#clock').onclick=()=>{const date=$('#clock small');date.hidden=!date.hidden;};
$('#hideReview').onclick=()=>$('#reviewTools').hidden=true;
document.querySelectorAll('[data-review]').forEach(button=>button.onclick=()=>{const screen=button.dataset.review;$('#reviewTools').hidden=true;if(screen==='desktop')showDesktop();else if(screen==='launcher')openLauncher();else if(screen==='login'){$('#login').hidden=false;$('#password').focus();}else openApp(screen);});
document.addEventListener('keydown',event=>{if(event.key==='F1'){event.preventDefault();$('#reviewTools').hidden=!$('#reviewTools').hidden;}if(event.key==='Escape')closePopups();if((event.ctrlKey||event.metaKey)&&event.code==='Space'&&$('#login').hidden){event.preventDefault();openLauncher();}});
document.addEventListener('pointerdown',event=>{if(!event.target.closest('.popup,#notificationsButton,#soundButton,dialog')){ $('#notifications').hidden=true;$('#sound').hidden=true;$('#notificationsButton').setAttribute('aria-expanded','false');$('#soundButton').setAttribute('aria-expanded','false'); }});
let drag=null;$('#titlebar').onpointerdown=event=>{if(event.target.closest('button')||$('#appWindow').classList.contains('maximized'))return;const rect=$('#appWindow').getBoundingClientRect();drag={x:event.clientX-rect.left,y:event.clientY-rect.top};$('#titlebar').setPointerCapture(event.pointerId);};
$('#titlebar').onpointermove=event=>{if(!drag)return;$('#appWindow').style.left=Math.max(0,Math.min(innerWidth-160,event.clientX-drag.x))+'px';$('#appWindow').style.top=Math.max(0,Math.min(innerHeight-90,event.clientY-drag.y))+'px';};$('#titlebar').onpointerup=()=>drag=null;
