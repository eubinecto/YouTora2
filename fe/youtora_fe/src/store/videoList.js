import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        search: {
            query: null,
            language: null,
            perPage: 10
        },
        currentPage: 1,
        videoQueryResult: []


    },
    getters: {
        GET_SEARCH_QUERY: (state) => {return state.search.query},
        GET_SEARCH_LANGUAGE: (state) => {return state.search.language},
        GET_PER_PAGE: (state) => {return state.search.perPage},

        GET_VIDEO_LIST: (state) => {return state.videoQueryResult},

    },
    mutations: {
        CLEAR_SEARCH: (state) => {
            state.videoQueryResult = []
            state.search.query = ''
        },

        SET_SEARCH_QUERY: (state, query) => {state.search.query = query},
        SET_SEARCH_LANGUAGE: (state, language) => {state.search.language = language},
        SET_PER_PAGE: (state, perPage) => {state.search.perPage = perPage},

        SET_VIDEO_LIST: (state, videoList) => {state.videoQueryResult = videoList}

    },
    actions: {

        SEARCH_VIDEOS: async ({commit, state}) => {
            const targetLink = process.env.VUE_APP_API + '/youtora_tracks/search'
            const payloadParams = {
                "content": state.search.query,
                "caption_lang_code": state.search.language,
                "from": (state.currentPage - 1) * state.search.perPage + 1,
                "size": state.search.perPage
            }
            await axios.get(targetLink, {data: null, params: payloadParams})
                .then(function (response) {
                    if (response.status !== 200) {
                        alert('QUERY' + state.search.query + 'not in DB')
                        commit('CLEAR_SEARCH')
                    } else {
                        const searchResult = response.data
                        commit('SET_VIDEO_LIST',searchResult)
                    }
                })
            console.log(state.videoQueryResult)

        }
    },

})