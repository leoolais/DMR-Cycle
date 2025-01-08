document.addEventListener('DOMContentLoaded', function () {
  const scanButton = document.getElementById('scanButton');
  const scannerContainer = document.getElementById('scanner-container');
  const searchInput = document.getElementById('search_term');

  let scannerInitialized = false;


function startScanner() {
  Quagga.init({
      inputStream : {
      name : "Live",
          type : "LiveStream",
          target: document.querySelector('#scanner-viewport'), // Pass element to Quagga
          constraints: {
           width: 320,
           height: 240,
           facingMode: "environment"
          },
          area: {
           top: "0%",
           right: "0%",
           left: "0%",
           bottom: "0%"
         },
     },
      decoder : {
          readers : ["code_128_reader"]
      }
  }, function(err) {
      if (err) {
          console.log(err);
          return;
      }
          Quagga.start();
          scannerInitialized = true;
           scannerContainer.style.display = 'block';

  });
}

function stopScanner() {
Quagga.stop();
scannerContainer.style.display = 'none';
  scannerInitialized = false;
}

  Quagga.onDetected(function(result) {
      searchInput.value = result.codeResult.code;
      stopScanner();
  });


  scanButton.addEventListener('click', function(event) {
    event.preventDefault();
     if (!scannerInitialized) {
          startScanner();
     } else {
          stopScanner();
     }
  });
});