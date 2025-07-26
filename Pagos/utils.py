def validarTarjeta(N):
    T=""; par=0;impar=0;X=""
    if not N.isdigit():return 0
    if len(N) <14 or len(N)> 19: return 0
    for c in range(0,len(N),2):       
        X=str(int(N[c])*2)       
        if len(X)==2:   
            par+=( int(X[0]) + int(X[1]) )
        else:par+=int(X)
    for c in range(1,len(N),2):
        impar+=int(N[c])
    if (par+impar)%10!=0:return 0
    if int(N[0:2])>49 and int(  N[0:2])<56:T="**MasterCard**"
    if N[0:2]=="34" or N[0:2]==37:T="**America Express**"
    if N[0]=="4":T="**VISA**"
    if N[0:2] in ["60","62","64","65"]:T="**Discover**"   
    return 1
