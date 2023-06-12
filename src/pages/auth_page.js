import * as React from 'react';
import Avatar from '@mui/material/Avatar';
import Button from "@mui/material/Button";
import CssBaseline from '@mui/material/CssBaseline';
import TextField from '@mui/material/TextField';
import Link from '@mui/material/Link';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import config from "../config";
import {useNavigate} from "react-router";

export default function AuthPage() {

    const navigate = useNavigate();

    const set_user_status = status => {
        localStorage.setItem(config.user_status, status)
    }

    const set_user_id = id => {
        localStorage.setItem(config.user_id, id)
    }

    const submitHandler = e => {
        e.preventDefault();
        const data = new FormData(e.currentTarget);
        fetch(
            `https://${config.backend_addr}/user/login`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json;charset=utf-8',
                },
                credentials: "include",
                body: JSON.stringify({
                    login: data.get('login'),
                    password: data.get('password'),
                })
            }
        )
            .then(async response => {
                if (response.ok) {
                    response = await response.json()
                    console.log(response)
                    set_user_status(true)
                    set_user_id(response.data.id)
                    navigate("/")
                } else {
                    throw Error(`Something went wrong: code ${response.status}`)
                }
            })
            .catch(error => {
                console.log(error)
            })
    }

    return (
        <Container component="main" maxWidth="xs">
            <CssBaseline />
            <Box
                sx={{
                    marginTop: 8,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                }}
            >
                <Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
                    <LockOutlinedIcon />
                </Avatar>
                <Typography component="h1" variant="h5">
                    Авторизация
                </Typography>
                <Box component="form" onSubmit={submitHandler} noValidate sx={{ mt: 1 }}>
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        id="login"
                        label="Логин"
                        name="login"
                        autoComplete="Логин"
                        autoFocus
                    />
                    <TextField
                        margin="normal"
                        required
                        fullWidth
                        name="password"
                        label="Пароль"
                        type="password"
                        id="password"
                        autoComplete="Пароль"
                    />
                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{ mt: 3, mb: 2 }}
                    >
                        Войти
                    </Button>
                    <Grid container>
                        <Grid item>
                            <Link href="/reg" variant="body2">
                                {"Нет аккаунта? Зарегестрируйтесь"}
                            </Link>
                        </Grid>
                    </Grid>
                </Box>
            </Box>
        </Container>
    );
}