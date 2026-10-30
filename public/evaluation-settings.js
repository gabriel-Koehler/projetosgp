export function versionNames(kind, count) {
  const colors=['Azul','Verde','Amarela','Vermelha','Branca','Rosa','Laranja','Roxa','Cinza','Marrom'];
  return Array.from({length:count},(_,index)=>{
    if(kind==='numbers')return String(index+1);
    if(kind==='colors')return colors[index%colors.length]+(index>=colors.length?' '+(Math.floor(index/colors.length)+1):'');
    let value=index+1,name='';
    while(value){value--;name=String.fromCharCode(65+value%26)+name;value=Math.floor(value/26);}
    return name;
  });
}
