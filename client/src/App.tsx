import { Routes, Route } from 'react-router-dom'
import Admin from './pages/Admin'
import Course from './pages/Course'
import Landing from './pages/Landing'
import Login from './pages/Login'
import MatesSearch from './pages/MatesSearch'
import Resource from './pages/Resource'
import Subject from './pages/Subject'
import SubjectTree from './pages/SubjectTree'
import Tree from './pages/Tree'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/admin" element={<Admin />} />
      <Route path="/login" element={<Login />} />
      <Route path="/mates-search" element={<MatesSearch />} />
      <Route path="/tree" element={<Tree />} />
      <Route path="/course" element={<Course />} />
      <Route path="/resource" element={<Resource />} />
      <Route path="/subject/:id" element={<Subject />} />
      <Route path="/subject-tree/:id_materia" element={<SubjectTree />} />
    </Routes>
  )
}
