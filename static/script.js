let currentLength=7;
let attempts=[];
let lastResults=null;
let currentPage = 1;
let pageSize = 50;
const states=["gray","yellow","green"];

function createBoard(){
    currentLength=parseInt(document.getElementById("length").value);
    let board=document.getElementById("board");
    board.innerHTML="";
    for(let i=0;i<currentLength;i++){
        let input=document.createElement("input");
        input.className="letter";
        input.maxLength=1;
        input.dataset.state="gray";
        input.onclick=()=>changeState(input);
        board.appendChild(input);
    }
}

function changeState(box){
    let index=(states.indexOf(box.dataset.state)+1)%states.length;
    box.dataset.state=states[index];
    box.className="letter "+states[index];
}

function addAttempt(){
    let boxes=document.querySelectorAll("#board .letter");
    let word="",colors=[];
    for(let box of boxes){
        let letter=box.value.trim();
        if(letter===""){
            alert("Completa todas las letras");
            return;
        }
        word+=letter.toLowerCase();
        colors.push(box.dataset.state);
    }
    attempts.push({word,colors});
    renderAttempts();
    clearBoard();
}

function renderAttempts(){
    let container=document.getElementById("attempts");
    container.innerHTML="";
    attempts.forEach((attempt,index)=>{
        let row=document.createElement("div");
        row.className="attempt-row";

        let wordContainer=document.createElement("div");
        wordContainer.className="attempt-word";

        for(let i=0;i<attempt.word.length;i++){
            let box=document.createElement("div");
            box.textContent=attempt.word[i].toUpperCase();
            box.className="attempt-letter "+attempt.colors[i];
            wordContainer.appendChild(box);
        }

        row.appendChild(wordContainer);

        let remove=document.createElement("button");
        remove.textContent="✖";
        remove.className="delete-attempt";
        remove.onclick=()=>{
            attempts.splice(index,1);
            renderAttempts();
        };

        row.appendChild(remove);
        container.appendChild(row);
    });
}

function clearBoard(){
    document.querySelectorAll("#board .letter").forEach(box=>{
        box.value="";
        box.dataset.state="gray";
        box.className="letter";
    });
}

function clearAll(){
    attempts=[];
    renderAttempts();
    clearBoard();
    document.getElementById("results").innerHTML="";
    document.getElementById("stats").innerHTML="";
}

function solveWordle(){
    fetch("/solve",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            length:currentLength,
            attempts:attempts,
            accent:document.getElementById("accent").value
        })
    })
    .then(r=>r.json())
    .then(data=>{
        lastResults=data;
        showResults(lastResults);
    });
}

function showResults(data){

    let stats=document.getElementById("stats");

    stats.innerHTML=`
        <p>Palabras restantes: <b>${data.count}</b></p>
        <p>Reducción: <b>${data.reduction}%</b></p>
    `;

    let words=[...data.words];

    let order=document.getElementById("sortResults").value;

    if(order==="alphabet"){

        words.sort((a,b)=>
            a.word.localeCompare(b.word,"es")
        );

    }else{

        words.sort((a,b)=>{

            if(a.score!==b.score)
                return b.score-a.score;

            return a.word.localeCompare(b.word,"es");

        });

    }

    pageSize=parseInt(
        document.getElementById("pageSize").value
    );

    let totalPages=Math.max(
        1,
        Math.ceil(words.length/pageSize)
    );

    if(currentPage>totalPages)
        currentPage=totalPages;

    let start=(currentPage-1)*pageSize;

    let end=Math.min(
        start+pageSize,
        words.length
    );

    let visibleWords=
        words.slice(start,end);

    document.getElementById(
        "pageInfo"
    ).innerHTML=

        words.length===0
        ?

        "No se encontraron palabras."

        :

        `Mostrando <b>${start+1}</b>–<b>${end}</b> de <b>${words.length}</b> palabras`;



    let list=document.getElementById("results");

    list.innerHTML="";



    visibleWords.forEach(item=>{

        let li=document.createElement("li");

        let stars="⭐";

        if(item.score>=6)
            stars="⭐⭐⭐⭐⭐";

        else if(item.score>=5)
            stars="⭐⭐⭐⭐";

        else if(item.score>=4)
            stars="⭐⭐⭐";

        else if(item.score>=2)
            stars="⭐⭐";

        li.textContent=
            item.word+
            " "+
            stars;

        list.appendChild(li);

    });



    document.getElementById(
        "prevPage"
    ).disabled=currentPage===1;



    document.getElementById(
        "nextPage"
    ).disabled=currentPage===totalPages;

}

window.onload=()=>{

    createBoard();

    document
        .getElementById("sortResults")
        .addEventListener(
            "change",
            ()=>{
                currentPage=1;
                if(lastResults)
                    showResults(lastResults);
            }
        );

    document
        .getElementById("pageSize")
        .addEventListener(
            "change",
            ()=>{
                currentPage=1;
                if(lastResults)
                    showResults(lastResults);
            }
        );

    document
        .getElementById("prevPage")
        .addEventListener(
            "click",
            ()=>{

                if(currentPage>1){

                    currentPage--;

                    showResults(lastResults);

                }

            }
        );

    document
        .getElementById("nextPage")
        .addEventListener(
            "click",
            ()=>{

                currentPage++;

                showResults(lastResults);

            }
        );

};