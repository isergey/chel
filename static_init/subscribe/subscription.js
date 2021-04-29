// import Subject from './subject.js';

const template = `
    <li class="subscribe">
        <label class="subscribe__selector">
            <input v-model="subscribed" type="checkbox" @change="handleChange" /> {{ title }}
        </label>
        <ul class="subscribe__children" :v-show="children.length">
            <subscription 
                v-for="child in children" 
                :key="child.id" 
                :title="child.title" 
                :children="child.children" 
                v-model="child.subscribed"
           />
        </ul>
    </li>
`;
export default {
    name: 'subscription',
    props: {
        modelValue: {
            type: Boolean,
            default: false,
        },
        title: {
            type: String,
            required: true,
        },
        children: {
            type: Array,
            required: false,
            default: []
        },

    },
    emits: ['update:modelValue'],
    template,
    data() {
        return {
            subscribed: this.modelValue,
        }
    },
    methods: {
        handleChange() {
            if (this.children.length) {
                this.children.forEach((child) => {
                    child.subscribed = this.subscribed;
                })
            }
            this.$emit('update:modelValue', this.subscribed);

        }
    },
    watch: {
        modelValue(value) {
            if (this.subscribed !== value) {
                this.subscribed = value;
            }
        }
    }
}