import Button from "@mui/material/Button";
import "../App.css"
import * as React from "react";
import TextField from "@mui/material/TextField";
import {useState, useEffect, useRef} from "react";
import {useNavigate} from "react-router";
import config from "../config";
import DocsWebSocket from "../DocsWS";


function Main() {

    const socket = useRef()

    const navigate = useNavigate()
    const [doc_name_val, set_doc_name_val] = useState("");
    const [docs_list, set_docs_list] = useState([]);

    const create_doc = async () => {
        // TODO: создать новый документ
        fetch(
            `https://${config.backend_addr}/doc/create`,
            {
                body: JSON.stringify({
                    name: doc_name_val,
                    timestamp: new Date().toISOString()
                })
            }
        )
            .then(async response => {
                if (response.ok) {
                    response = await response.json()
                    console.log(response)
                    const new_id = response.data.id
                    navigate(`/doc/${new_id}`)
                } else {
                    throw Error(`Something went wrong: code ${response.status}`)
                }
            })
            .catch(error => {
                console.log(error)
            })
    }

    const get_docs_list = async () => {
        fetch(`https://${config.backend_addr}/doc/list`, {
            credentials: "include",
        })
            .then(async response => {
                if (response.ok) {
                    response = await response.json()
                    console.log(response)
                    set_docs_list(response.data.docs)
                } else {
                    throw Error(`Something went wrong: code ${response.status}`)
                }
            })
            .catch(error => {
                console.log(error)
            })
    }

    useEffect(() => {

        // socket.current = new DocsWebSocket(`ws://localhost:8080/connect/${1}?userID=${localStorage.getItem(config.user_id) || 88005553535}`, [], {
        //     credentials: "include"
        // })
        // socket.current.onopen = null
        // socket.current.onmessage_handler = null
        // socket.current.onclose = null
        // socket.current.onerror = null

        get_docs_list()


    }, [])

    return (
        <>
            <TextField
                margin="normal"
                id="doc_name"
                label="Название документа"
                name="doc_name"
                autoComplete="Тест1"
                value={doc_name_val}
                onChange={e => {
                    set_doc_name_val(e.target.value)
                }}
            />
            <Button
                type="submit"
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                onClick={create_doc}
            >
                Создать новый документ
            </Button>
            <br/>
            {docs_list.length === 0? <>Нет документов</>:
                docs_list.map((val, index) => {
                    return <Button
                        onClick={() => {
                            navigate(`/doc/${val.id}`)
                        }
                        }
                    >
                        {val.name}
                    </Button>
                })
            }
        </>
    )

}

export default Main
