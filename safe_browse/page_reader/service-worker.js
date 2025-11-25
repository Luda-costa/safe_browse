async function getCurrentTab() {
    let queryOptions = { active: true, lastFocusedWindow: true };
    let [tab] = await chrome.tabs.query(queryOptions);

    // Prepare data as your API expects
    const reqBody = JSON.stringify({ url: tab.url });

    // Make the request to your Flask API
    fetch("http://localhost:5000/verifica_url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: reqBody
    })
    .then(response => response.json())
    .then(data => {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icon.png',
    title: 'Resultado da URL',
    message: "Site " + data.classificacao + "\nSuspeitas:\n" + data.explicacao 
    });
  })  
    .catch(error => {
      console.error("Erro ao comunicar com a API:", error);
    });

    return tab;
}

getCurrentTab();


