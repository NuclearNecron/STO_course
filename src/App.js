import './App.css';
import {BrowserRouter} from "react-router-dom";
import {Route, Routes} from "react-router";
import Document from "./pages/document";
import AuthPage from "./pages/auth_page";
import RegPage from "./pages/reg_page";


function App() {
    return (
        <BrowserRouter basename="/" >
            <Routes>
                <Route path={"/doc"} element={<Document/>}/>
                <Route path={"/auth"} element={<AuthPage/>}/>
                <Route path={"/reg"} element={<RegPage/>}/>
            </Routes>
        </BrowserRouter>
    )
}

export default App;
