document.addEventListener('DOMContentLoaded', function () {

   // Barcode Generation and Printing
    const generateButton = document.getElementById('generateButton');
    const uniqueIdInput = document.getElementById('unique_id');
    const barcodeContainer = document.getElementById('barcodeContainer');
    const barcodeSVG = document.getElementById('barcode');
    const printButton = document.getElementById('printButton');


   if (generateButton) {
       generateButton.addEventListener('click', function(event){
        event.preventDefault();
        generateBarcode();
      });
   }

  function generateBarcode() {
      const uniqueId = uniqueIdInput.value;
       if (uniqueId){
            JsBarcode("#barcode", uniqueId, {
                format: "CODE128",
                displayValue: true,
                width: 2,
                height: 60,
                textMargin: 2
             });
              barcodeContainer.style.display = 'block';
       }

  }

    if (printButton) {
        printButton.addEventListener('click', function(){
         window.print();
        });
    }
// Scanner Code
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