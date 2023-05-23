import Button from "@mui/material/Button";
import "../App.css"
import * as React from "react";
import TextField from "@mui/material/TextField";
import {useState, useEffect, useRef} from "react";
import {useNavigate} from "react-router";
import config from "../config";
import {Card, CardActions, CardContent} from "@mui/material";
import Typography from "@mui/material/Typography";
import Link from "@mui/material/Link";


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
                method: "POST",
                headers:{
                    'Content-Type':'application/json;charset=utf-8'
                },
                credentials: "include",
                body: JSON.stringify({
                    name: doc_name_val,
                    timestamp: new Date().toISOString()
                }),
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

    const delete_doc = async (doc_id) => {
        fetch(`https://${config.backend_addr}/doc/${doc_id}`, {
            credentials: "include",
            method: "DELETE",
        })
            .then(async response => {
                if (response.ok) {
                    response = await response.json()
                    console.log(response)
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
            <div>
                <Button variant={"contained"} className={"button"}
                        onClick={e => {
                            navigate("/auth")
                        }}
                >Авторизоваться</Button>
                <Button variant={"contained"} className={"button"}
                        onClick={e => {
                            navigate("/reg")
                        }}
                >Зарегестрироваться</Button>
            </div>
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
                    return <Card sx={{ minWidth: 200 }}>
                        <CardContent>
                            <Typography variant="h5" component="div">
                                {val.name}
                            </Typography>
                            <Typography sx={{ mb: 1.5 }} color="text.secondary">
                                Последнее сохранение: {val.last_edited}
                            </Typography>
                            <Typography sx={{ mb: 1.5 }} color="text.secondary">
                                Владелец: {val.owner.nickname}
                            </Typography>
                        </CardContent>
                        <CardActions>
                            <Button size="small" onClick={() => {
                                navigate(`/doc/${val.id}`)
                            }
                            }>Перейти</Button>
                            <Button size="small" onClick={ async() => {
                                await delete_doc(val.id)
                            }
                            }>Удалить</Button>
                        </CardActions>
                    </Card>
                })
            }
        </>
    )

}

export default Main
