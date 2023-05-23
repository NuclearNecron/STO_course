import '../App.css';
import {useEffect, useRef, useState} from "react";
import {useParams} from "react-router";
import {TextField} from "@mui/material";
import DocsWebSocket from "../DocsWS";
import config from "../config";


function Document() {

    const {docID} = useParams();

    const [val, set_val] = useState("");
    const [have_doc, set_have_doc] = useState(false);
    const [last_edited, set_last_edited] = useState(null);
    const [ws_connected, set_ws_connected] = useState(false);
    const socket = useRef();

    //  Начало блока с функциями для поиска изменений в тексте и их отправки

    const find_diffrence_lr = (bigger, shorter) => {
        var  symbol_left = 0
        for (let i=0; i<shorter.length;i++){
            if (bigger[i]!==shorter[i]){
                break
            }
            symbol_left++
        }
        return symbol_left
    }

    const find_diffrence_right = (bigger, remained, position) => {
        var symbol = bigger.length - 1, correct =0
        for (let i=remained.length-1; i>-1;i--){
            if (bigger[symbol]!==remained[i]){
                break
            }
            symbol--
            correct++
        }
        return correct
    }

    const update_handler = async (old_doc, new_doc) => {
        // TODO: вставить после каждого лога рассылку по вебсокету
        console.log(old_doc)
        console.log(new_doc)
        if (new_doc.length>old_doc.length){
            const change_lenght = new_doc.length-old_doc.length
            const lr_diff = find_diffrence_lr(new_doc,old_doc)
            if (lr_diff === old_doc.length){
                const change_ = {
                    "add":true,"position":lr_diff,"symbol":new_doc.substring(lr_diff)
                }
                console.log(change_)
                await sendUpdate(change_)
            }
            else{
                const right_correct = find_diffrence_right(new_doc,old_doc.substring(lr_diff))
                const inline_same = lr_diff+right_correct
                if (old_doc.length- inline_same===0){
                    const change_ = {
                        "add":true,"position":lr_diff,"symbol":new_doc.substring(lr_diff,lr_diff+change_lenght)
                    }
                    console.log(change_)
                    await sendUpdate(change_)
                }
                else{
                    let change_ = {
                        "add":false,"position":lr_diff,"symbol":old_doc.substring(lr_diff,lr_diff+old_doc.length- inline_same)
                    }
                    console.log(change_)
                    await sendUpdate(change_)
                    change_ = {
                        "add":true,"position":lr_diff,"symbol":new_doc.substring(lr_diff,lr_diff+change_lenght+old_doc.length- inline_same)
                    }
                    console.log(change_)
                    await sendUpdate(change_)
                }
            }
        }else if (new_doc.length<old_doc.length){
            const change_lenght = old_doc.length -new_doc.length
            const lr_diff = find_diffrence_lr(old_doc,new_doc)
            if (lr_diff === old_doc.length){
                const change_ = {
                    "add":false,"position":lr_diff,"symbol":old_doc.substring(lr_diff)
                }
                console.log(change_)
                await sendUpdate(change_)
            }
            else{
                const right_correct = find_diffrence_right(old_doc,new_doc.substring(lr_diff))
                const inline_same = lr_diff+right_correct
                if (new_doc.length- inline_same===0){
                    const change_ = {
                        "add":false,"position":lr_diff,"symbol":old_doc.substring(lr_diff,lr_diff+change_lenght)
                    }
                    console.log(change_)
                    await sendUpdate(change_)
                }
                else{
                    let change_ = {
                        "add":false,"position":lr_diff,"symbol":old_doc.substring(lr_diff,lr_diff+change_lenght+new_doc.length- inline_same)
                    }
                    console.log(change_)
                    await sendUpdate(change_)
                    change_ = {
                        "add":true,"position":lr_diff,"symbol":new_doc.substring(lr_diff,lr_diff+new_doc.length- inline_same)
                    }
                    console.log(change_)
                    await sendUpdate(change_)
                }
            }}else{
            const lr_diff = find_diffrence_lr(new_doc,old_doc)
            if (lr_diff === new_doc.length){
                let change_ = {
                    "add":false,"position":lr_diff,"symbol":old_doc.substring(lr_diff)
                }
                console.log(change_)
                await sendUpdate(change_)
                change_ = {
                    "add":true,"position":lr_diff,"symbol":new_doc.substring(lr_diff)
                }
                console.log(change_)
                await sendUpdate(change_)
            }
            else{
                const right_correct = find_diffrence_right(new_doc,old_doc.substring(lr_diff))
                const inline_same = lr_diff+right_correct
                let change_ = {
                    "add":false,"position":lr_diff,"symbol":old_doc.substring(lr_diff,lr_diff+new_doc.length- inline_same)
                }
                console.log(change_)
                await sendUpdate(change_)
                change_ = {
                    "add":true,"position":lr_diff,"symbol":new_doc.substring(lr_diff,lr_diff+new_doc.length- inline_same)
                }
                console.log(change_)
                await sendUpdate(change_)
            }}

    }

    //  Конец блока с функциями для поиска изменений в тексте и их отправки

    const sendUpdate = async update => {
        const msg = {
            type: "UPDATE",
            payload: {
                update: update,
                timestamp: new Date().toISOString(),
            }
        }
        socket.current.send(JSON.stringify(msg))
    }

    const onopen_handler = (e) => {
        set_ws_connected(true)
        console.log("Успешное подключение к websocket!")
        console.log(e)
    }

    const onmessage_handler = (event) => {
        const msg_ = JSON.parse(event.data) // парсинг сообщения в json
        console.log(msg_.payload.update)

        if (msg_.type === "DOCUMENT_DELETED") {
            // TODO: документ удален - обработать
        }
        else if (msg_.type === "DISCONNECTED") {
            // TODO: отняли права - заблочить текстбокс + как-то предупредить?
        }
        else if (msg_.type === "CONNECTED") {
            // Пока не юзается
        }
        else if (msg_.type === "SERVICE") {
            // Пока не юзается
        }
        else if (msg_.type === "UPDATE") {
            let change_ = msg_.payload.update
            let timestamp_ = msg_.payload.timestamp
            // TODO: заменить логику применения изменения
            set_val(`${msg_.payload.update}`)
        }
    }

    const onclose_handler = (e) => {
        set_ws_connected(false)
        console.log("Произошло отключение от websocket!")
        console.log(e)
    }

    const onerror_handler = (e) => {
        console.log("websocket: произошла ошибка!")
        console.log(e)
    }

    useEffect(() => {

        // Получение инфы о доке (нужно для временной метки последнего редактирования)
        fetch(
            `https://${config.backend_addr}/doc/${docID}`,
            {
                credentials: "include",
            }
        )
            .then(async raw_response => {
                if (raw_response.ok) {
                    const response = await raw_response.json()
                    console.log(response)
                    set_last_edited(response.data.last_edited)
                } else {
                    throw Error(`Something went wrong: code ${raw_response.status}`)
                }
            })

        // Получение содержания дока
        fetch(
            `https://${config.backend_addr}/doc/get/${docID}`,
            {
                credentials: "include",
            }
        )
            .then(async raw_response => {
                if (raw_response.ok) {
                    const response = await raw_response.json()
                    console.log(response)
                    set_val(response.data.res)
                    set_have_doc(true)
                } else {
                    throw Error(`Something went wrong: code ${raw_response.status}`)
                }
            })

    }, [])

    useEffect(() => {

        if (have_doc) {

            socket.current = new DocsWebSocket(`wss://${config.webscoket_addr}/connect/${docID}`)
            socket.current.onopen = onopen_handler
            socket.current.onmessage_handler = onmessage_handler
            socket.current.onclose = onclose_handler
            socket.current.onerror = onerror_handler
        }

    }, [have_doc])

    return(
        <>
            {!ws_connected? <>No connection to WebSocket Server!</>:
                <>
                    <TextField
                        id="val"
                        label={"Пишем здесь"}
                        variant="outlined"
                        value={val}
                        onChange={event => {
                            event.preventDefault()
                            console.log(event.target.value)
                            update_handler(val, event.target.value)
                            // set_val(event.target.value)  // не должно тут юзаться
                            // sendUpdate(event.target.value)   // не должно тут юзаться
                        }}
                        style={{width:"100%"}}
                        multiline={true}
                        rows={10}
                    />
                </>
            }
        </>
    )
}

export default Document;
