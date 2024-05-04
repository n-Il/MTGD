//this code creates all the variables we use
let pageSize = 50;
let resultStartIndex = 0;
let resultEndIndex = Math.min(pageSize,results.length);
//this code sets up the text at the top
document.getElementById("query").innerText = "using query: " + query;
document.getElementById("total").innerText = "collected("+collectionUnique+" Unique). Filtered from "+scryfallTotalResults+" total results from Scryfall ";
//setup the drop down text options
updatePageSizes();
//setup the drop down on-clicks
setupDropDownClicks();
//create the initial images
setupImages(resultStartIndex,resultEndIndex);
//set the initial bounds text
updateBounds();

/****************************************/
/****************************************/
/****************************************/

function updateBounds(){
    document.getElementById("bounds").innerText = resultStartIndex.toString() + "-" + resultEndIndex.toString() +" of "+ results.length.toString();
}

function reload(){
    document.body.scrollTop = document.documentElement.scrollTop = 0;
    location.reload();
}

//this is called by the pageSize buttons within the drop-down and they send themselves
function setPageSize(button){
    pageSize = Number(button.innerText);
    updatePageSizes();
    resultEndIndex = Math.min(resultStartIndex+pageSize,results.length);
    updateBounds();
    setupImages(resultStartIndex,resultEndIndex);
}

function updatePageSizes(){
    let pageSizeNumbers = [15,25,50,100];//dont change the number of pageSizeNumbers
    let pageSizes = document.getElementsByClassName("pagesize");
    let pscounter = 0;
    for (let i = 0; i < 4; i++){
        if (pageSizeNumbers[i] != pageSize){
            pageSizes[pscounter].innerText = pageSizeNumbers[i];     
            pscounter += 1;
        }
    }
    Array.from(document.getElementsByClassName("dropdownbutton")).forEach(inst=>inst.innerText = pageSize+" Per Page");
}

function dropDownFunction(){
    document.getElementById("subdropdown").classList.toggle("show");
}

function setupDropDownClicks(){
    window.onclick = function(event){
        if (!event.target.matches('.dropdownbutton')){
            let dropdowns = document.getElementsByClassName("dropdowncontent");
            for (let i = 0; i< dropdowns.length; i++){
                let openDropDown = dropdowns[i];
                if (openDropDown.classList.contains('show')){
                    openDropDown.classList.remove('show');
                }
            }
        }
    }
}

function setupImages(start,end){
    let resultImages = document.getElementById("results");
    resultImages.innerHTML = '';
    for (let i = start; i < end;i++){
        let image = document.createElement('img');
        image.src = results[i][0];
        image.style['cursor'] = "pointer";
        image.style['width']  = '20%';
        image.addEventListener("click",function(){window.open(results[i][1]),"_blank"});
        resultImages.appendChild(image);
    }
}

function prev(){
    document.body.scrollTop = document.documentElement.scrollTop = 0;
    if (resultStartIndex != 0){
        resultStartIndex -= pageSize;
        resultEndIndex = resultStartIndex+pageSize
        updateBounds();
        setupImages(resultStartIndex,resultEndIndex);
    }
}

function next(){
    document.body.scrollTop = document.documentElement.scrollTop = 0;
    if ((resultStartIndex+pageSize) < results.length){
        resultStartIndex += pageSize;
        if ((results.length) > (resultEndIndex+pageSize)){
            resultEndIndex += pageSize;
        }else{
            resultEndIndex = results.length
        }
        updateBounds();
        setupImages(resultStartIndex,resultEndIndex);
    }
}
