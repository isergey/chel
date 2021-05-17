import Subscription from './subscription.js';

const template = `
<div class="subscriptions">
    <div class="subscriptions__loader" v-show="!loaded">Загрузка данных...</div>
    <div class="subscriptions__error alert alert-danger" v-show="error.length">{{ error }}</div>
    <div class="subscriptions__content" v-show="loaded">
        <ul class="subscriptions__subscriptions">
            <subscription 
                v-for="subscription in subscriptions" 
                :key="subscription.id"
                :title="subscription.title"
                :children="subscription.children"
                v-model="subscription.subscribed"
            />
        </ul>
        <div class="subscriptions__params">
            <input class="form-control" type="email" v-model="email"/>
        </div>
    </div>

    <div class="subscriptions__toolbar" v-show="subscriptions.length">
        <div class="subscribtions__save-message alert alert-success" v-show="saveMessage.length" >{{ saveMessage }}</div>
        <button v-show="!isSaving" class="btn" type="button" @click="handleSave">Сохранить</button>
        <button v-show="isSaving" class="btn" type="button">Сохранение...</button>
        <button class="btn subscriptions__unsubscribe_btn" type="button" @click="handleUnsubscribe">Отписаться от всех рассылок</button>
    </div>
</div>
`;

async function loadData() {
    const response = await fetch('/ru/subscribe/get_subscribes/');
    return await response.json();
}

async function saveData(subscribtions) {
    const response = await fetch('/ru/subscribe/set_subscribes/', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X_KEY': new URLSearchParams(window.location.search).get('key') || undefined,
        },
        body: JSON.stringify(subscribtions)
    });
    if (response.status >= 400) {
        throw Error('Ошибка сохраенния параметров подписки')
    }
}

export default Vue.createApp({
    template,
    components: {
        Subscription,
    },
    data() {
        return {
            loaded: true,
            isSaving: false,
            error: '',
            saveMessage: '',
            email: '',
            subscriptions: []
        }
    },
    mounted() {
        this.loadData();
    },
    methods: {
        async loadData() {
            this.loaded = false;
            this.error = '';
            try {
                const data = await loadData();
                this.email = data.email;
                this.subscriptions = data.subscriptions;
            } catch (e) {
                this.error = String(e);
            } finally {
                this.loaded = true;
            }
        },
        async handleSave() {
            this.error = '';
            this.isSaving = true;
            this.saveMessage = '';
            try {
                await saveData({
                    email: this.email,
                    subscriptions: this.subscriptions,
                });
                this.saveMessage = 'Параметры рассылки сохранены';
            } catch (e) {
                this.error = String(e.message);
            } finally {
                this.isSaving = false;
            }
            // console.log(JSON.stringify(this.subscriptions, undefined, 2));
        },
        async handleUnsubscribe() {
            this.subscriptions.forEach(subscription => {
                subscription.subscribed = false;
                subscription.children.forEach(child => {
                    child.subscribed = false;
                });
            });
        }
    }
});