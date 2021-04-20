(function () {
    const subscribeTpl = `
        <div class="subscribe">
            Продписки 
            <div v-show="!loaded" class="subscribe_loader">Загрузка подписок...</div>
        </div>
    `;

    function Subscribe(name, subscribed) {
        return {
            name: name,
            subscribed: subscribed
        }
    }

    const SubscribeApp = {
        template: subscribeTpl,
        data() {
            return {
                subscribes: [],
                loaded: true
            }
        },
        mounted() {
            this.loadSubscribes();
        },
        methods: {
            loadSubscribes() {
                 this.loaded = false;
            }
        }
    }
    Vue.createApp(SubscribeApp).mount('#subscriptions')
})();