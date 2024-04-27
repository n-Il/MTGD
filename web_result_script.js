//results = [...
//let fiftyImages = document.querySelector(".results");
let fiftyImages= document.getElementById("results");
fiftyImages.style['padding-left'] = '20%';
fiftyImages.style['padding-right'] = '20%';
let docFrag = document.createDocumentFragment();
docFrag.id = "results";
lookupResults = [];
for (let i = 0; i < 50;i++){
    let image = document.createElement('img');
    image.src = results[i][0];
    image.style['cursor'] = "pointer";
    image.onClick = function(){window.open(results[i][1]),"_blank"};
    image.addEventListener("click",image.onClick)
    image.style['width']  = '20%';
    lookupResults[i] = image;
    docFrag.appendChild(image);
}
fiftyImages.appendChild(docFrag);
resultStartIndex = 0;
resultEndIndex = 50;
document.getElementById("bounds").innerText = resultStartIndex.toString() + "-" + resultEndIndex.toString() +" of "+ results.length.toString();
let prevClass = document.getElementsByClassName("prev");
let nextClass = document.getElementsByClassName("next");
let reloadClass = document.getElementsByClassName("reload");
for (var i = 0; i < reloadClass.length;i++){
    reloadClass[i].addEventListener("click",function(){
        document.body.scrollTop = document.documentElement.scrollTop = 0;
        //console.log("reload"); this gets eaten
        location.reload();
});}

for (var i = 0; i < prevClass.length;i++){
    prevClass[i].addEventListener("click",function(){
        document.body.scrollTop = document.documentElement.scrollTop = 0;
        console.log("prev");
        if (resultStartIndex != 0){
            resultStartIndex -= 50;
            resultEndIndex -= 50;
            document.getElementById("bounds").innerText = resultStartIndex.toString() + "-" + resultEndIndex.toString() +" of "+ results.length.toString();
            let resultsChildren = Array.from(document.getElementById("results").children);
            for (let i = resultStartIndex; i < resultEndIndex;i++){
                lookupResults[i%50].src = results[i][0];
                lookupResults[i%50].removeEventListener("click",lookupResults[i%50].onClick)
                lookupResults[i%50].onClick = function(){window.open(results[i][1]),"_blank"};
                lookupResults[i%50].addEventListener("click",lookupResults[i%50].onClick)
            }

        }
});}
for (var i = 0; i < nextClass.length;i++){
    nextClass[i].addEventListener("click",function(){
        document.body.scrollTop = document.documentElement.scrollTop = 0;
        console.log("next");
        //I DONT FEEL LIKE WRITING THE ERROR HANDLING OR CHECKING FOR THE TOP HALF BUT IT MUST BE DONE
        resultStartIndex += 50;
        resultEndIndex += 50;
        document.getElementById("bounds").innerText = resultStartIndex.toString() + "-" + resultEndIndex.toString() +" of "+ results.length.toString();
        for (let i = resultStartIndex; i < resultEndIndex;i++){
            lookupResults[i%50].src = results[i][0];
            lookupResults[i%50].removeEventListener("click",lookupResults[i%50].onClick)
            lookupResults[i%50].onClick = function(){window.open(results[i][1]),"_blank"};
            lookupResults[i%50].addEventListener("click",lookupResults[i%50].onClick)
    }
});}

