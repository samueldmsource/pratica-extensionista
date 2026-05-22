"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

// 1. Função auxiliar de conversão totalmente restaurada
function expandRecorrencia(data: any[]) {
    return data.flatMap((item) => {
        const rec = item.recorrencia

        const base = {
            id: item.id,
            nome: item.nome,
            responsavel: item.responsavel,
            local: item.local,
        }

        if (rec?.tipo === "Unica") {
            return [
                {
                    ...base,
                    recorrencia: "Única",
                    dia: rec.data,
                    horarioInicio: rec.horarioInicio,
                    horarioFim: rec.horarioFim,
                },
            ]
        }

        if (rec?.tipo === "Semanal") {
            return Object.entries(rec.horarios || {}).map(([dia, h]: any) => ({
                ...base,
                recorrencia: "Semanal",
                dia: dia,
                horarioInicio: h.horarioInicio,
                horarioFim: h.horarioFim,
            }))
        }

        return [{ ...base, recorrencia: "Não especificada" }]
    })
}

// 2. Componente principal da página com retorno visual válido
export default function AtividadesPage() {
    const [activities, setActivities] = useState<any[]>([])
    const router = useRouter()

    useEffect(() => {
        fetch("http://localhost:8000/activities/")
            .then(res => res.json())
            .then(data => {
                const expanded = expandRecorrencia(data)
                setActivities(expanded)
            })
            .catch(err => console.error("Erro ao carregar atividades", err))
    }, [])

    return (
        <div className="p-8 max-w-4xl mx-auto">
            <h1 className="text-2xl font-bold mb-4">Painel de Atividades</h1>
            <p className="text-gray-600 mb-6">Lista de atividades integradas com o Back-end.</p>
            
            <div className="bg-white shadow rounded-lg p-4">
                {activities.length === 0 ? (
                    <p className="text-gray-500">Nenhuma atividade encontrada ou carregando...</p>
                ) : (
                    <ul className="divide-y divide-gray-200">
                        {activities.map((act, index) => (
                            <li key={index} className="py-3">
                                <p className="font-semibold text-lg text-black">{act.nome}</p>
                                <p className="text-sm text-gray-600">Responsável: {act.responsavel} | Local: {act.local}</p>
                                <p className="text-xs text-blue-600 mt-1">Tipo: {act.recorrencia} ({act.dia})</p>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    )
}
