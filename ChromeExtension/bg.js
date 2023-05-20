
async function getCreds(sitename) {
  let response = await fetch("http://localhost:8000/"+sitename);
  let data = await response.json();
  return data;
}

chrome.runtime.onMessage.addListener(messageHandle);

function messageHandle (request, sender, senderResponse) {
  if (request.message == 'save_text') {
    data= getCreds(request.sitename)
    data.then(injestToContent)
    // { message: "Creds",data:creads}
  }
}
function injestToContent(data){
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      chrome.tabs.sendMessage(tabs[0].id,data);
    })}
