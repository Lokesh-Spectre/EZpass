chrome.runtime.onMessage.addListener((response,sender,sendResponse)=>{
  if (response.found == true){
    fill(response)
  }
})
function fill(response){

  usr=document.getElementById(response.user_id)
  usr.value=response.username
  passwd_element=document.getElementById(response.passwd_id)
  passwd_element.value=response.passwd
}
site =window.location.href.slice(8).split('/')[0]
chrome.runtime.sendMessage({ message: "save_text",sitename:site})





