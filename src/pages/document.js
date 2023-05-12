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
    const [ws_connected, set_ws_connected] = useState(false);
    const socket = useRef();

    const sendUpdate = async update => {
        const msg = {
            type: "UPDATE",
            payload: {
                "update": update
            }
        }
        socket.current.send(JSON.stringify(msg))
    }

    const onopen_handler = (e) => {
        set_ws_connected(true)
        console.log("Вы успешно подключились!")
        console.info(e)
    }

    const onmessage_handler = (event) => {
        const msg_ = JSON.parse(event.data)
        console.log(msg_.payload.update)
        set_val(`${msg_.payload.update}`)
    }

    const onclose_handler = (e) => {
        set_ws_connected(false)
        console.log("Вы отключились :(")
        console.info(e)
    }

    const onerror_handler = (e) => {
        console.log("Произошла ошибка!")
        console.info(e)
    }

    const getDocument = async doc_id => {
        const raw_response = await fetch(
            `https://${config.backend_addr}/doc/get/${docID}`,
            {
                credentials: "include",
            }
        )
        if (raw_response.ok) {
            const response = await raw_response.json()
            // response выше имеет тип строки???
            set_val(`${response}`)
            set_have_doc(true)
        }
    }

    useEffect(() => {

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
                    // response выше имеет тип строки???
                    set_val(response.data.res)
                    set_have_doc(true)
                } else {
                    throw Error(`Something went wrong: code ${raw_response.status}`)
                }
            })

    }, [])

    useEffect(() => {

        if (have_doc) {
            socket.current = new DocsWebSocket(`ws://${config.webscoket_addr}/connect/${docID}?userID=${localStorage.getItem(config.user_id) || 88005553535}`)
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
                            set_val(event.target.value)
                            sendUpdate(event.target.value)
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
